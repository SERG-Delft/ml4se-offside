import numpy as np
import tensorflow as tf

def main() -> None:
    X = np.load("X.npy")
    Y = np.load("Y.npy")



    print(np.mean(Y))


    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(384,)))
    model.add(tf.keras.layers.Dense(384, activation="relu"))
    model.add(tf.keras.layers.Dense(384, activation="relu"))
    model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


    #print(Y)
    print(model.summary())
    model.fit(X, Y, epochs=5)
    #print(model.predict(X))




if __name__ == '__main__':
    main()