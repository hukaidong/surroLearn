#!/usr/bin/env python
# encoding: utf-8

import os
import tensorflow as tf

from .constructor import Constructor
from .executor import Executor
from .maxout import stack_max_out
from .utils import Time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main(filename=None, save_dir="./save", compatiable=True):

    if compatiable:
        from .data import compatible_load
        inputs, references = compatible_load(filename)

    m = stack_max_out(1000, 10, 6)
    c = Constructor(m, inputs, references)
    g = c.training_bake()

    with tf.Session() as sess:
        e = Executor(sess, g, c.save_list, save_dir)
        for i in range(4):
            e.train()

            e.evaluate(*c.test_pipe())


def lambda_inc(filename, lrange1, lrange2, steps):
    from .data import compatible_load
    from .formulations import l2_lambda
    from .utils import tensor_geo_interval_range

    inputs, references = compatible_load(filename)

    m = stack_max_out(1000, 10, 6)
    c = Constructor(m, inputs, references)
    lt = tensor_geo_interval_range(lrange1, lrange2, steps)
    c.regularize_formulate = l2_lambda(lt)

    g = c.training_bake()
    s = steps // 50
    t = Time(s)
    with tf.Session() as sess:
        e = Executor(sess, g, c.save_list, "")
        for i in range(s):
            e.train()
            e.evaluate(*c.test_pipe())
            print("Estimate time finishing", t.tick())