# Lancer cette cette commande dans le terminal avant de lancer vos scripts python,
# cela permets d'utiliser le GPU (carte graphique):
# source activate GPU
#
# Lancer ensuite vos code avec: python main_incomplet.py
#
# Ou alors lancer un terminal Python avec: ipython
# puis lancer votre script avibec: run main_incomplet.py
# Cela vous permettra de debeuger et de taper vos commandes sans avoir
# a relancer tout le script.


# Lrairies pour réseau de neurones
from keras.datasets import mnist # hand written digits
from keras.layers import Input, Activation
from keras.layers.core import Dropout, Lambda
from keras.layers.convolutional import Conv2D, Conv2DTranspose, UpSampling2D, Convolution2D
from keras.layers.pooling import MaxPooling2D
from keras.layers.merge import concatenate, Add
from keras.models import Model
from keras import optimizers, losses
from keras.models import load_model 

import numpy as np
import matplotlib.pyplot as plt          

# Commenter à l'INSA
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"


## Load data
# On recupere les images
# x: Matrices de taille 28x28 avec des valeurs de 0 à 255.
# y: chiffre auquel correspond l'image. On utilise pas y ici.

(x_train, _), (x_test, _) = mnist.load_data()


# Degradation

sigma_noise = 90
sigma_flou = 20 # Le flou va s'etaler sur environ 3*sigma_flou pixels

# ### Choisir entre l'ajout de bruit et l'ajout de flou
# # On ajoute un flou stationaire et du bruit gaussien
n1,n2=x_train.shape[1],x_train.shape[2]
lin1=np.linspace(-n1/2,n1/2,n1)
lin2=np.linspace(-n2/2,n2/2,n2)
XX,YY=np.meshgrid(lin1,lin2)
G=np.exp(-(XX**2+YY**2)/(sigma_flou**2))
G/=np.sum(G)
Ghat=np.fft.fft2(np.fft.fftshift(G))

# y_train = np.zeros((x_train.shape[0],x_train.shape[1],x_train.shape[2]))
# for k in range(x_train.shape[0]):
#   # Convolution en u et v = F^{-1}(F(u)*F(v)), ou * est le produit terme à terme et F est l'opérateur de tranformée de fourier
#     y_train[k]=np.fft.ifft2(np.fft.fft2(x_train[k])*Ghat)+sigma_noise*np.random.randn(n1,n2) 
# y_test = np.zeros((x_test.shape[0],x_test.shape[1],x_test.shape[2]))
# for k in range(x_test.shape[0]):
#     y_test[k]=np.fft.ifft2(np.fft.fft2(x_test[k])*Ghat)+sigma_noise*np.random.randn(n1,n2) 

# Inpainting
#tmp = x_train.copy()
#tmp[:,10:20,:]=0
#y_train = tmp + sigma_noise*np.random.randn(x_train.shape[0],x_train.shape[1],x_train.shape[2]) 
#tmp = x_test.copy()
#tmp[:,10:20,:]=0
#y_test = tmp + sigma_noise*np.random.randn(x_test.shape[0],x_test.shape[1],x_test.shape[2]) 

# On ajoute du bruit gaussien

y_train = x_train + sigma_noise*np.random.randn(x_train.shape[0],x_train.shape[1],x_train.shape[2]) 
y_test = x_test + sigma_noise*np.random.randn(x_test.shape[0],x_test.shape[1],x_test.shape[2]) 

# Afficher quelques images
fig = plt.figure(1)
col = 10 #Number of colmuns
for i in range(1, col+1):
  # Number of rows = 2
  # Position = i 
  fig.add_subplot(2, col, i)
  plt.imshow(x_train[i],interpolation='nearest')
  # Position = i+ col 
  fig.add_subplot(2, col, i+col)
  plt.imshow(y_train[i],interpolation='nearest')
#plt.show()
plt.savefig('fig_1.png')

# Mettre donnees en forme pour passer dans le réseau
x_train_ext = np.expand_dims(x_train,3) # ajoute une dimension a x_train à la position 3
y_train_ext = np.expand_dims(y_train,3)  
x_test_ext = np.expand_dims(x_test,3)  
y_test_ext = np.expand_dims(y_test,3) 

# Roughly DONE: comprendre chaque fonctions
# def model_simple():
#   init = Input(shape=(None, None,1)) # une image noir et blanc de taille non détérminée
# # Version visuelle des convolutions! http://cs231n.github.io/assets/conv-demo/index.html
#   x = Convolution2D(16, (3, 3), activation='relu', padding='same')(init) 
#   x = MaxPooling2D((2, 2))(x)
#   x = Convolution2D(32, (3, 3), activation='relu', padding='same')(x) 
#   x = MaxPooling2D((2, 2))(x)
#   x = Convolution2D(64, (3, 3), activation='relu', padding='same')(x)
#   x = Convolution2D(32, (3, 3), activation='relu', padding='same')(x)
#   x = UpSampling2D()(x)
#   x = Convolution2D(16, (3, 3), activation='relu', padding='same')(x)
#   x = UpSampling2D()(x)
#   x = Convolution2D(1, (3, 3), activation='relu', padding='same')(x) # permet d'avoir une image noir et blanc en sortie

#   # Autres fonctions potentiellement utiles:
#   # x = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same') (x)
#   # x = concatenate([x1, x2])
#   # x = Dropout(0.5)(x)
#   # m1 = Add()([x1, x2])

#   NN = Model(init, x)
#   return NN

# model = model_simple() # charge le modele
# model.summary() # affiche les proprietes du modele

# # autres fonctions cout existent: binary_crossentropy,... https://keras.io/losses/
# loss = losses.mse
# # autres techniques d'optimisation existent: sgd, adagrad,... https://keras.io/optimizers/
# optim = optimizers.Adam()
# # Compile le modele
# model.compile(loss=loss,
#               optimizer=optim,
#               metrics=['mse']) # pour visualisation

# # Entrainement
# # TODO: jouer avec nombre d'epochs, batch_size
# epochs = 10 # nombre de pas de descente dans l'optimisation
# batch_size = 128
# out_train = model.fit(y_train_ext, x_train_ext,
#           batch_size=batch_size,
#           epochs=epochs,
#           verbose=1,
#           validation_data=(y_test_ext, x_test_ext))

# model.save('model1.h5')  # Pour enregistrer le réseau model

model = load_model('model1.h5') # Pour charger le réseau model

# DONE: evaluer le réseau sur la partie test du jeu de données (pourquoi jamais sur le train?), 
# utiliser la fonction 'predict' pour faire obtenir la sortie du réseau de neurone (model.predict)
predictions = model.predict(y_test_ext)

score = model.evaluate(y_test_ext, x_test_ext, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

#Save info of this model
#f=open("model1_info.txt", "w")
#f.write(model.summary())
#f.write("Model 1: Convo + Maxpooling + UpSampling => Test lost: %3f   Test accuracy: %3f " %(score[0],score[1]))
#f.close()

with open('model1.txt','w') as fh:
    # Pass the file handle in as a lambda function to make it callable
    model.summary(print_fn=lambda x: fh.write(x + '\n'))

loss_train = out_train.history['loss']
loss_test = out_train.history['val_loss']
mse_train = out_train.history['mse']

plt.figure(2)
plt.plot(loss_train,label='training')
plt.plot(loss_test,label='validation')
plt.title('Loss')
plt.legend()
#plt.show()
plt.savefig('loss_1.png')

# Afficher quelques images

# DONE: afficher les resultats sur la meme figure comme au debut
fig = plt.figure(3)
col = 10
rows = 3
for i in range(1, col+1):
  # Position = i 
  fig.add_subplot(rows, col, i)
  plt.imshow(np.squeeze(predictions[i], axis=(2,)),interpolation='nearest')
  # Position = i+ col 
  fig.add_subplot(rows, col, i+col)
  plt.imshow(x_test[i],interpolation='nearest')
  fig.add_subplot(rows, col, i+2*col)
  plt.imshow(y_test[i],interpolation='nearest')
#plt.show()
plt.savefig('final_1.png')

def SNR(x_ref,x):
  x_ref_vect = x_ref.flatten()
  x_vect = x.flatten()
  res=-20*np.log10(np.linalg.norm(x_ref_vect-x_vect)/np.linalg.norm(x_vect)+1e-15)
  return res

  
#Append SNR output to a file to compare SNR of all models
def Append(data, file_name, model_number):
  f=open(file_name, "a+")
  f.write("Signal to Noise ratio of model %d is : %3f " %(model_number,data))
  f.close()
  
Append(SNR(x_test, np.squeeze(predictions)), 'SNR.txt', 1)


  
