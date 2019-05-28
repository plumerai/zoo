import pytest
import functools
import larq_zoo as lqz
import os
import numpy as np
from tensorflow import keras


def keras_test(func):
    """Function wrapper to clean up after TensorFlow tests.
    # Arguments
        func: test function to clean up after.
    # Returns
        A function wrapping the input function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        keras.backend.clear_session()
        return output

    return wrapper


def parametrize(func):
    func = keras_test(func)
    return pytest.mark.parametrize(
        "app,last_feature_dim", [(lqz.BinaryAlexNet, 256), (lqz.BiRealNet, 512)]
    )(func)


@keras_test
def test_prediction():
    file = os.path.join(os.path.dirname(__file__), "fixtures", "elephant.jpg")
    img = keras.preprocessing.image.load_img(file)
    img = keras.preprocessing.image.img_to_array(img)
    img = lqz.preprocess_input(img)
    model = lqz.BiRealNet()
    preds = model.predict(np.expand_dims(img, axis=0))

    # Test correct label is in top 3 (weak correctness test).
    names = [p[1] for p in lqz.decode_predictions(preds, top=3)[0]]
    assert "African_elephant" in names


@parametrize
def test_basic(app, last_feature_dim):
    model = app(weights=None)
    assert model.output_shape == (None, 1000)


@parametrize
def test_no_top(app, last_feature_dim):
    model = app(weights=None, include_top=False)
    assert model.output_shape == (None, None, None, last_feature_dim)


@parametrize
def test_no_top_variable_shape_1(app, last_feature_dim):
    input_shape = (None, None, 1)
    model = app(weights=None, include_top=False, input_shape=input_shape)
    assert model.output_shape == (None, None, None, last_feature_dim)


@parametrize
def test_no_top_variable_shape_4(app, last_feature_dim):
    input_shape = (None, None, 4)
    model = app(weights=None, include_top=False, input_shape=input_shape)
    assert model.output_shape == (None, None, None, last_feature_dim)
