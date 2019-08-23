Neural Network Model using Chainer
====
Predict for Japan Academy Film Prize by neural network model using framework Chainer.

## Description
A neural network model built using Chainer 
that outputs the probability of winning the top prize of Japan Academy Film Award
by inputting data on the five best movies of the year.

https://www.japan-academy-prize.jp/

## Requirement
* python 3.6.0

* chainer 6.2.0
* numpy 1.17.0
* optuna 0.14.0
* pandas 0.25.0

## Usage
Create `data/dataframes/data.pkl` and every pkl files in `data/std_data`.

```
python neural_network_model.py

python predict.py
```

### Example

```
python optimize_parameter.py
```

```
[Best trial]
  Value:  0.44096583127975464
  Params: 
    n_layers: 2
    n_units_l0: 121
    batchsize: 1411
    n_units_l1: 37
  User attrs:
    main/loss: 0.585271418094635
    validation/main/loss: 0.44096583127975464
    epoch: 1006
    iteration: 117
    elapsed_time: 1.5739546479999973
```

```
python neural_network_model.py [--batchsize] 1411 [--epoch] 1000
python predict.py
```

## Install
git clone https://github.com/kondounagi/japanese_movies_dataset/

cd japanese_movies_dataset/neo_review/scripts/nn
