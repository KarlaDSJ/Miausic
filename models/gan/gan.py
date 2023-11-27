from tensorflow.keras.layers import Dense, Reshape, Dropout, LSTM, Bidirectional
from tensorflow.keras.layers import BatchNormalization, LeakyReLU
from tensorflow.keras.models import Sequential
#from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.legacy import Adam #Para MAC
import numpy as np
import matplotlib.pyplot as plt


class GAN():
    def __init__(self, dataset, shape=(100,1), latent_dim=100):
        self.latent_dim = latent_dim
        self.dataset = dataset
        self.disc_loss = []
        self.gen_loss =[]
        self.g_model = self.define_generator(shape)
        self.d_model = self.define_discriminator(shape)
        self.gan_model = self.define_gan()

    # Definimos la red que identificara si la muestra dada es generada por la otra red o una real
    def define_discriminator(self, in_shape):
        """Red encargada de decidir si lo generado es real o fake"""
        model = Sequential()
        model.add(LSTM(512, input_shape=in_shape, return_sequences=True))
        model.add(Bidirectional(LSTM(512)))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(256))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(100))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dropout(0.5))
        model.add(Dense(1, activation='sigmoid'))

        opt = Adam(learning_rate=0.00002, beta_1=0.5)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
        return model

    #Definimos la red que crea pistas musicales
    def define_generator(self, seq_shape):
        """Red encargada de generar piezas musicales"""
        model = Sequential()
        model.add(Dense(256, input_dim = self.latent_dim))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(np.prod(seq_shape), activation='tanh'))
        model.add(Reshape(seq_shape))
        model.summary()

        return model

    def define_gan(self):
        """Red generativa (un generador y un discriminador)"""
        self.d_model.trainable = False
        model = Sequential()
        model.add(self.g_model)
        model.add(self.d_model)
        opt = Adam(learning_rate=0.0002, beta_1=0.5)
        model.compile(loss='binary_crossentropy', optimizer=opt)
        return model
    
    def plot_loss(self):
        plt.plot(self.disc_loss, c='red')
        plt.plot(self.gen_loss, c='blue')
        plt.title("GAN Loss per Epoch")
        plt.legend(['Discriminator', 'Generator'])
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.savefig('objects/GAN_Loss_per_Epoch_final.png')
        plt.show()
        plt.close()

    def summarize_performance(self, epoch, d_loss, g_loss):
        """
        Nos muestra el rendimiento de la red que discrimina y la que genera
        Guarda el modelo de generación
        """
        ##Falta mostrar bien las métricas y agregar las que el profe pidio
        print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))
        self.disc_loss.append(d_loss[0])
        self.gen_loss.append(g_loss)
        if epoch % 50 == 0:
            filename = 'objects/generator_model.h5'
            self.g_model.save(filename)

    def prepare_sequences(self, notes, n_vocab):
        """Creamos las secuencias para la red"""
        sequence_length = 100
        #Obtenemos todas las notas y las mapeamos a un número
        note_to_int = dict((note, number) for number, note in enumerate(set(notes)))
        network_input = []
        # Creamos las secuencias
        for i in range(0, len(notes) - sequence_length, 1):
            sequence_in = notes[i:i + sequence_length]
            network_input.append([note_to_int[char] for char in sequence_in])

        # Hacemos reshape para que sea compatible con la re LSTM y normalizamos (-1 a 1)
        network_input = np.reshape(network_input, (len(network_input), sequence_length, 1))
        network_input = (network_input - float(n_vocab) / 2) / (float(n_vocab) / 2)

        return network_input

    def generate_real_samples(self, n_samples):
        """Tomamos pista reales"""
        train_notes = np.array(self.dataset['pitch'])
        n_vocab = len(train_notes)
        X_train = self.prepare_sequences(train_notes, n_vocab)
        ix = np.random.randint(0, len(X_train), n_samples)
        X = X_train[ix]
        y = np.ones((n_samples, 1))
        return X, y
    
    def generate_latent_points(self,n_samples):
        """Generamos ruido"""
        x_input = np.random.randn(self.latent_dim * n_samples)
        x_input = x_input.reshape(n_samples, self.latent_dim)
        return x_input

    def generate_fake_samples(self, n_samples):
        """Generamos una pista con el modelo generador"""
        x_input = self.generate_latent_points(n_samples)
        X = self.g_model.predict(x_input)
        y = np.zeros((n_samples, 1))
        return X, y

    def train(self, n_epochs=20, n_batch=128):
        """
        Entrenamos la red GAN
        """
        half_batch = int(n_batch / 2)

        for i in range(n_epochs):
            #Entrenamos al discriminador
            X_real, y_real = self.generate_real_samples(half_batch)
            X_fake, y_fake = self.generate_fake_samples(half_batch)
            X, y = np.vstack((X_real, X_fake)), np.vstack((y_real, y_fake))
            d_loss = self.d_model.train_on_batch(X, y)
            # Entrenamos el generador 
            X_gan = self.generate_latent_points(n_batch)
            y_gan = np.ones((n_batch, 1))
            g_loss = self.gan_model.train_on_batch(X_gan, y_gan)

            
            self.summarize_performance(i, d_loss, g_loss)
        
        self.plot_loss()


