#!/usr/bin/env python
# encoding: utf-8

import os
import tensorflow as tf

from datetime import datetime


class Executor(object):
    def __init__(self, sess, graph, save_list, save_dir, evaluate_only=False):
        """

        With a finalized graph and a session given, run training / testing process

        Args:

        sess:
            Tensorflow session object

        graph:
            finalized graph

        save_list:
            list of parameters needs to be saved / restored

        save_dir:
            directory path to save the model.

        evaluate_only:
            if true, only get predict related nodes from graph

        """

        self.sess = sess
        self.graph = graph
        self.save_list = save_list
        self.save_dir = save_dir

        self.saver = tf.train.Saver(save_list)
        self.global_step = tf.get_variable("global_step")
        self.ref_rmse = tf.get_variable("ref_rmse")
        self.inputs = tf.get_variable("inputs")
        self.reference = tf.get_variable("reference")

        if not evaluate_only:
            self.global_init = tf.get_operation_by_name("global_init")
            self.epoch_init = tf.get_operation_by_name("epoch_init")
            self.train_op = tf.get_operation_by_name("train_op")
            self.global_step_inc = tf.get_operation_by_name("global_step_inc")

            self.sess.run(self.global_init)

    def global_step(self):
        return self.sess.run(self.global_step)

    def train(self, epochs=50):
        if self.evaluate_only:
            raise UnableToTrainError("Attempt to run training process on a "
                                     "evaluating model.")
        self.sess.run(self.epoch_init)
        for i in range(epochs):
            try:
                while True:
                    self.sess.run(self.train_op)
            except tf.errors.OutofRangeError:
                pass

        global_step = self.global_step()
        print(datetime.now(), "Training on step ", global_step, " finished.")

    def evaluate(self, inputs, reference, msg):
        sample = {
            self.inputs: inputs,
            self.reference: reference,
        }

        rmse = self.sess.run(self.ref_rmse, feed_dict=sample)
        print(datetime.now(), "Evaluating on ", msg, ": ", rmse)

        return rmse

    def predict(self, inputs):
        sample = {self.inputs: inputs}
        prediction = self.sess.run(self.reference, feed_dict=sample)

        return prediction

    def save_model(self):
        print(datetime.now(), ":Saving checkpoints...")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.saver.save(self.sess, self.save_dir, global_step=self.global_step)

    def load_model(self):
        ckpt = tf.train.latest_checkpoint(self.save_dir)
        if ckpt:
            print(datetime.now(), ": Loading checkpoints from ", ckpt)
            self.saver.restore(self.sess, ckpt)
            return True
        else:
            print(datetime.now(), ": [!] Loading checkpoints fail")
            return False


class UnableToTrainError(Exception):
    pass
