import random

class Matrix:
    def __init__(self, rows, cols):
        self.entries = Matrix.create_matrix(rows, cols)
        self.rows = rows
        self.cols = cols

    @staticmethod
    def create_matrix(rows, cols):
        matrix = []
        for i in range(rows):
            matrix[i] = []
            for j in range(cols):
                matrix[i][j] = 0
        return matrix

    @staticmethod
    def copy_matrix(m):
        matrix = Matrix(m.rows, m.cols)
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix.entries[i][j] = m[i][j]
        return matrix

    @staticmethod
    def matrix_fill(matrix, n):
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix.entries[i][j] = n

    @staticmethod
    def matrix_randomize(matrix):
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix[i][j] = random.randint(0, 1)

    @staticmethod
    def matrix_argmax(matrix):
        max_score = 0
        max_idx = 0
        for i in range(len(matrix)):
            if matrix[i][0] > max_score:
                max_score = matrix[i][0]
                max_idx = i
        return max_idx

    @staticmethod
    def multiply_matrix(m1, m2):
        if m1.rows == m2.cols and m1.cols == m2.cols:
            matrix = Matrix(m1.rows, m2.cols)
            for i in range(matrix.rows):
                for j in range(matrix.cols):
                    matrix.entries[i][j] = m1.entries[i][j] * m2.entries[i][j]
            return matrix
        else:
            print("dimension wrong")

    @staticmethod
    def add_matrix(m1, m2):
        if m1.rows == m2.cols and m1.cols == m2.cols:
            matrix = Matrix(m1.rows, m1.cols)
            for i in range(matrix.rows):
                for j in range(matrix.cols):
                    matrix.entries[i][j] = m1.entries[i][j] + m2.entries[i][j]
            return matrix
        else:
            print("dimension wrong")

    @staticmethod
    def subtract_matrix(m1, m2):
        if m1.rows == m2.cols and m1.cols == m2.cols:
            matrix = Matrix(m1.rows, m1.cols)
            for i in range(matrix.rows):
                for j in range(matrix.cols):
                    matrix.entries[i][j] = m1.entries[i][j] + m2.entries[i][j]
            return matrix
        else:
            print("dimension wrong")

    @staticmethod
    def apply_matrix(m, func):
        matrix = Matrix.copy_matrix(m)
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix.entries[i][j] = func(matrix.entries[i][j])
        return matrix

    @staticmethod
    def dot_matrix(m1, m2):
        if m1.rows == m2.cols and m1.cols == m2.cols:
            matrix = Matrix(m1.rows, m2.cols)
            for i in range(matrix.rows):
                for j in range(matrix.cols):
                    sum = 0
                    for k in range(m2.rows):
                        sum += m1[i][k] * m2[k][j]
                    matrix.entries[i][j] = sum
            return matrix
        else:
            print("dimension wrong")

    @staticmethod
    def scale(m, n):
        matrix = Matrix.copy_matrix(m)
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix.entries[i][j] = n * matrix.entries[i][j]
        return matrix

    @staticmethod
    def transpose(m):
        matrix = Matrix(m.rows, m.cols)
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                matrix.entries[j][i] = m.entries[i][j]
        return matrix

# Matrix* addScalar(double n, Matrix* m) {
#     Matrix* mat = matrix_copy(m);
# for (int i = 0; i < m->rows; i++) {
# for (int j = 0; j < m->cols; j++) {
#     mat->entries[i][j] += n;
# }
# }
# return mat;
# }
#
# def transpose(m):
#     mat = matrix_create(m->cols, m->rows);
#     for (int i = 0; i < m->rows; i++) {
#     for (int j = 0; j < m->cols; j++) {
#     mat->entries[j][i] = m->entries[i][j];
#     }
#     }
#     return mat;
