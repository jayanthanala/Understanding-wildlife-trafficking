#2Sparks

from d3m import container
import datetime
from pathlib import Path
import os
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import pyarrow as pa
import sys
import nltk
from nltk.tokenize import word_tokenize

from pyspark import SparkContext, SparkConf
from pyspark.sql.functions import format_string,col, when, coalesce
cf = SparkConf()
cf.set("spark.submit.deployMode","client")
sc = SparkContext.getOrCreate(cf)
from pyspark.sql import SparkSession
spark = SparkSession \
	    .builder \
	    .config("spark.some.config.option", "some-value") \
	    .getOrCreate()
spark.conf.set("spark.sql.repl.eagerEval.enabled",True)
sc.setLogLevel('OFF')


file_path_list = ['/shared/CS-GY-6513/projects/WildLife/processed-data-oct/*.parquet']
df = spark.read.parquet(*file_path_list)

df2 = df.select([col(c).alias(
        c.replace( '(', '')
        .replace( ')', '')
        .replace( ',', '')
        .replace( ';', '')
        .replace( '{', '')
        .replace( '}', '')
        .replace( '\n', '')
        .replace( '\t', '')
        .replace( ' ', '_')
    ) for c in df.columns])
    
df3 = spark.read.schema(df2.schema).parquet(*file_path_list)
df3.printSchema()
df3.show(1,False)
df3.count()

df4 = df3.dropDuplicates()
df4.count()

animals = spark.read.format('csv').options(header='true',inferschema='true').load('/user/ja4874_nyu_edu/datasets/03_gbif_common_names.csv')
animalsArray = animals.select("gbif_common_name","English name of Language","French name of Language","German name of Language").toPandas().values.reshape(-1)
animalsArrayUnique = np.unique(animalsArray)

//fix this
def extract_animals(text):
    tokenized_text = word_tokenize(text.lower())
    return [word for word in tokenized_text if word in animalsArrayUnique]

df['animals'] = df['text'].apply(extract_animals)
