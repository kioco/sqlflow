import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
import random

data = {
    'c1': [random.random() for _ in range(300)],
    'c2': [random.random() for _ in range(300)],
    'c3': [random.random() for _ in range(300)],
    'c4': [random.random() for _ in range(300)],
    'c5': [random.random() for _ in range(300)],
    'target': [random.randint(0,2) for _ in range(300)]
}
dataframe = pd.DataFrame.from_dict(data)

train, test = train_test_split(dataframe, test_size=0.2)
train, val = train_test_split(train, test_size=0.2)
print(len(train), 'train examples')
print(len(val), 'validation examples')
print(len(test), 'test examples')

# A utility method to create a tf.data dataset from a Pandas Dataframe
def df_to_dataset(dataframe, shuffle=True, batch_size=1):
    dataframe = dataframe.copy()
    labels = dataframe.pop('target')
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    return ds

batch_size = 32 # A small batch sized is used for demonstration purposes
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

feature_columns = [tf.feature_column.numeric_column(header) for header in ['c1', 'c2', 'c3', 'c4', 'c5']]

class DNNClassifier(tf.keras.Model):
    def __init__(self, feature_columns, hidden_units, n_classes):
        """DNNClassifier
        :param feature_columns: feature columns.
        :type feature_columns: list[tf.feature_column].
        :param hidden_units: number of hidden units.
        :type hidden_units: list[int].
        :param n_classes: List of hidden units per layer.
        :type n_classes: int.
        """
        super(DNNClassifier, self).__init__()

        # combines all the data as a dense tensor
        self.feature_layer = tf.keras.layers.DenseFeatures(feature_columns)
        self.hidden_layers = []
        for hidden_unit in hidden_units:
            self.hidden_layers.append(tf.keras.layers.Dense(hidden_unit))
        self.prediction_layer = tf.keras.layers.Dense(n_classes, activation='softmax')

    def call(self, inputs):
        x = self.feature_layer(inputs)
        for hidden_layer in self.hidden_layers:
            x = hidden_layer(x)
        return self.prediction_layer(x)

    def default_optimizer(self):
        """Default optimizer name. Used in model.compile."""
        return 'adam'

    def default_loss(self):
        """Default loss function. Used in model.compile."""
        return 'categorical_crossentropy'

    def default_training_epochs(self):
        """Default training epochs. Used in model.fit."""
        return 5

    def prepare_prediction_column(self, prediction):
        """Return the class label of highest probability."""
        return prediction.argmax(axis=-1)

model = DNNClassifier(feature_columns=feature_columns, hidden_units=[10, 10], n_classes=3)
model.compile(optimizer=model.default_optimizer(), loss=model.default_loss())

is_training = False
if is_training:
    model.fit(train_ds, validation_data=val_ds, epochs=model.default_training_epochs(), verbose=0)
    model.save_weights('my_model.h5')
    print("Done training.")
else:
    model.predict(test_ds)
    model.load_weights('my_model.h5')
    prediction = model.predict(test_ds)
    print(model.prepare_prediction_column(prediction))
    print("Done predictiing.")