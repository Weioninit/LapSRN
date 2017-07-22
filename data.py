import tensorflow as tf
import argument
from os.path import join
from PIL import Image
import os


def get_all_file(path, endFormat, withPath=True):
    """
        寻找path 路径下以 在endFormate数组中出现的文件格式的文件
    Args:
        path:  路径
        endFormat: [] 包含这些类型的 format
        withPath: 返回的路径是否带之间的路径
    Returns:
        所有符合条件的文件名
    """
    dir = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if True in [file.endswith(x) for x in endFormat]:
                filename = join(path, file) if withPath else file
                dir.append(filename)

    return dir


def batch_queue_for_training(data_path):
    num_channel = argument.options.input_channel
    image_height = argument.options.height
    image_width = argument.options.width
    batch_size = argument.options.batch_size
    threads_num = argument.options.num_threads
    min_queue_examples = argument.options.min_after_dequeue

    filename_queue = tf.train.string_input_producer(get_all_file(path=data_path, endFormat=['jpg']))
    file_reader = tf.WholeFileReader()
    _, image_file = file_reader.read(filename_queue)
    patch = tf.image.decode_jpeg(image_file, num_channel)
    patch = tf.image.convert_image_dtype(patch, dtype=tf.float32)

    image_HR8 = tf.random_crop(patch, [image_height, image_width, num_channel])

    image_HR4 = tf.image.resize_images(image_HR8, [int(image_height / 2), int(image_width / 2)],
                                       method=tf.image.ResizeMethod.BICUBIC)
    image_HR2 = tf.image.resize_images(image_HR8, [int(image_height / 4), int(image_width / 4)],
                                       method=tf.image.ResizeMethod.BICUBIC)
    image_LR = tf.image.resize_images(image_HR8, [int(image_height / 8), int(image_width / 8)],
                                      method=tf.image.ResizeMethod.BICUBIC)

    low_res_batch, high2_res_batch, high4_res_batch, high8_res_batch = tf.train.shuffle_batch(
        [image_LR, image_HR2, image_HR4, image_HR8],
        batch_size=batch_size,
        num_threads=threads_num,
        capacity=min_queue_examples + 3 * batch_size,
        min_after_dequeue=min_queue_examples)

    return low_res_batch, high2_res_batch, high4_res_batch, high8_res_batch


def save_image(image, path):
    with open(path, "wb") as file:
        file.write(image)


def batch_queue_for_training_mkdir():
    num_channel = argument.options.input_channel
    image_height = argument.options.height
    image_width = argument.options.width
    batch_size = argument.options.batch_size
    threads_num = argument.options.num_threads

    filename_queue = tf.train.string_input_producer(argument.options.get_file_list())
    file_reader = tf.WholeFileReader()
    _, image_file = file_reader.read(filename_queue)
    patch = tf.image.decode_jpeg(image_file, num_channel)
    patch = tf.image.convert_image_dtype(patch, dtype=tf.float32)

    image_HR8 = tf.random_crop(patch, [image_height, image_width, num_channel])

    image_HR4 = tf.image.resize_images(image_HR8, [int(image_height / 2), int(image_width / 2)],
                                       method=tf.image.ResizeMethod.BICUBIC)
    image_HR2 = tf.image.resize_images(image_HR8, [int(image_height / 4), int(image_width / 4)],
                                       method=tf.image.ResizeMethod.BICUBIC)
    image_LR = tf.image.resize_images(image_HR8, [int(image_height / 8), int(image_width / 8)],
                                      method=tf.image.ResizeMethod.BICUBIC)

    low_res_batch, high2_res_batch, high4_res_batch, high8_res_batch = tf.train.batch(
        [image_LR, image_HR2, image_HR4, image_HR8],
        batch_size=batch_size,
        num_threads=threads_num,
        capacity=3 * batch_size)

    filename_queue.close()

    return low_res_batch, high2_res_batch, high4_res_batch, high8_res_batch


def dataTest():
    low_res_batch, high2_res_batch, high4_res_batch, high8_res_batch = batch_queue_for_training_mkdir()
    images = []
    for i in range(16):
        temp = tf.image.convert_image_dtype(high2_res_batch[i], dtype=tf.uint8)
        temp = tf.image.encode_jpeg(temp)
        images.append(temp)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        tf.train.start_queue_runners(sess=sess)
        low = sess.run(images)
        for i in range(16):
            save_image(low[i], './test/low' + str(i) + '.jpg')


def get_image_info():
    paths = argument.options.get_file_list()
    for path in paths:
        im = Image.open(path)
        height = min(im.size[1], im.size[0])
        width = max(im.size[1], im.size[0])
        print(width, height)

# if __name__ == '__main__':
#     for i in range(1000):
#         get_image_info()
