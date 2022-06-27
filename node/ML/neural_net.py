import numpy as np


class NeuralNetwork:
    def __init__(self, input, hidden, output, lr):
        self.hidden_weights = np.random.rand(input, hidden)
        self.output_weights = np.random.rand(hidden, output)
        self.input = input
        self.hidden = hidden
        self.output = output
        self.learning_rate = lr

    def sigmoid(self, mat):
        return 1 / (1 + np.exp(-1 * mat))

    def sigmoid_prime(self, mat):
        ones = np.ones(mat.shape)
        return (ones - mat) * mat

    def softmax(self, Z):
        # calculates the softmax value for a matrix
        # collapses the matrix into one row
        A = np.exp(Z) / sum(np.exp(Z))
        return A

    def forward_prop(self, X):
        Z1 = np.dot(self.hidden_weights, X)
        A1 = self.sigmoid(Z1)
        Z2 = np.dot(self.output_weights, A1)
        A2 = self.sigmoid(Z2)
        return Z1, A1, Z2, A2

    def back_prop(self, Z1, A1, Z2, A2, X, Y):
        E2 = Y - A2
        E1 = np.dot(self.output_weights.T, E2)

        new_output_weights = self.output_weights + self.learning_rate * np.dot(E2 * self.sigmoid_prime(A2), A1.T)
        new_hidden_weights = self.hidden_weights + self.learning_rate * np.dot(E1 * self.sigmoid_prime(A1), X.T)

        return new_hidden_weights, new_output_weights

    def train(self, X, Y):
        Z1, A1, Z2, A2 = self.forward_prop(X)
        W1, W2 = self.back_prop(Z1, A1, Z2, A2, X, Y)
        self.hidden_weights = W1
        self.output_weights = W2

    def predict(self, X):
        Z1, A1, Z2, A2 = self.forward_prop(X)
        res = self.softmax(A2)
        return res
