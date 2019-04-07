Title: Calling PySpark code from a Scala Spark job
Date: 2019-04-05 14:00
Tags: spark, scala, python, pyspark, py4j
Status: draft

https://stackoverflow.com/questions/51910607/how-to-use-a-pyspark-udf-in-a-scala-spark-project
- how to use pyspark UDF in a spark scala project



https://github.com/spark-jobserver/spark-jobserver/blob/master/job-server-extras/src/main/scala/spark/jobserver/python/PythonJob.scala

Calling python / pyspark from scala Spark; should be able to see this in Spark job server

> Python code
- https://github.com/spark-jobserver/spark-jobserver/tree/master/job-server-python/src/python
- https://github.com/spark-jobserver/spark-jobserver/blob/master/job-server-python/src/python/sparkjobserver/api.py#L126
    - accessing named objects
- https://github.com/spark-jobserver/spark-jobserver/blob/master/job-server-python/src/python/sparkjobserver/subprocess.py
    - python side
    - start python in subprocess, accessing py4J gateway started by JVM process

> Scala code
- https://github.com/spark-jobserver/spark-jobserver/tree/master/job-server-extras/src/main/scala/spark/jobserver/python
    - scala code
- https://github.com/spark-jobserver/spark-jobserver/blob/master/job-server-extras/src/main/scala/spark/jobserver/python/PythonJob.scala
    - starts the python subprocess to communicate with it
    - shuts down gateway after job finishes

> Idea
- we can keep the python code running on a thread
- can communicate with it (tell it to run a command via a reference)
    - feed it in commands on stdin
- reference named values (cached rdds)
- as long as the amt of data passed back and forth is minimal, performance should be ok



> Demo
- make a small project where I can demo this on github

> Tests

https://github.com/spark-jobserver/spark-jobserver/blob/master/job-server-extras/src/test/scala/spark/jobserver/python/PythonSparkContextFactorySpec.scala
- example test of getting spark context

> Limitations

- performance implications of switching languages
- having to cache dataframe to access via a named variable
- when is this good ot bad

