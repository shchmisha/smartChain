from matrix import Matrix
import math


class NeuralNetwork:
    def __init__(self, input, hidden, output, lr):
        self.hidden_weights = Matrix(input, hidden)
        self.output_weights = Matrix(hidden, output)
        Matrix.matrix_randomize(self.hidden_weights)
        Matrix.matrix_randomize(self.output_weights)
        self.input = input
        self.hidden = hidden
        self.output = output
        self.learning_rate = lr

    def sigmoid(self, mat):
        return 1 / (1 + math.exp(-1 * mat))

    def sigmoid_prime(self, mat):
        ones = Matrix(mat.rows, mat.cols)
        Matrix.matrix_fill(ones, 1)
        return Matrix.multiply_matrix(mat, Matrix.subtract_matrix(ones, mat))

    def softmax(self, Z):
        total = 0
        for i in range(Z.rows):
            for j in range(Z.cols):
                total += math.exp(Z.entries[i][j])
        mat = Matrix(Z.rows, Z.cols)
        for i in range(mat.rows):
            for j in range(mat.cols):
                mat.entries[i][j] = math.exp(Z.entries[i][j]) / total
        return mat

    def forward_prop(self, X):
        Z1 = Matrix.dot_matrix(self.hidden_weights, X)
        A1 = Matrix.apply_matrix(Z1, self.sigmoid)
        Z2 = Matrix.dot_matrix(self.output_weights, A1)
        A2 = Matrix.apply_matrix(Z2, self.sigmoid)
        return Z1, A1, Z2, A2

    def back_prop(self, Z1, A1, Z2, A2, X, Y):
        E2 = Matrix.subtract_matrix(Y, A2)
        E1 = Matrix.dot_matrix(Matrix.transpose(self.output_weights), E2)

        new_output_weights = Matrix.add_matrix(self.output_weights, Matrix.scale(self.learning_rate, Matrix.dot_matrix(
            Matrix.multiply_matrix(E2, self.sigmoid_prime(A2)), Matrix.transpose(A1))))
        new_hidden_weights = Matrix.add_matrix(self.hidden_weights, Matrix.scale(self.learning_rate, Matrix.dot_matrix(
            Matrix.multiply_matrix(E1, self.sigmoid_prime(A1)), Matrix.transpose(X))))

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

    def train_batch_imgs(self):
        pass
