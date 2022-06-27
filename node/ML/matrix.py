import random


def create_matrix(rows, cols):
    matrix = []
    for i in range(rows):
        matrix[i] = []
        for j in range(cols):
            matrix[i][j] = 0
    return matrix


def copy_matrix(m):
    matrix = create_matrix(len(m), len(m[0]))
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = m[i][j]
    return matrix


def matrix_fill(matrix, n):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = n


def matrix_randomize(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = random.randint(0, 1)


def matrix_argmax(matrix):
    max_score = 0
    max_idx = 0
    for i in range(len(matrix)):
        if matrix[i][0] > max_score:
            max_score = matrix[i][0]
            max_idx = i
    return max_idx


def multiply_matrix(m1, m2):
    if len(m1) == len(m2) and len(m1[0]) == len(m2):
        matrix = create_matrix(len(m1), len(m1[0]))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                matrix[i][j] = m1[i][j] * m2[i][j]
        return matrix
    else:
        print("dimension wrong")


def add_matrix(m1, m2):
    if len(m1) == len(m2) and len(m1[0]) == len(m2):
        matrix = create_matrix(len(m1), len(m1[0]))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                matrix[i][j] = m1[i][j] + m2[i][j]
        return matrix
    else:
        print("dimension wrong")


def subtract_matrix(m1, m2):
    if len(m1) == len(m2) and len(m1[0]) == len(m2):
        matrix = create_matrix(len(m1), len(m1[0]))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                matrix[i][j] = m1[i][j] - m2[i][j]
        return matrix
    else:
        print("dimension wrong")


def apply_matrix(m, func):
    matrix = copy_matrix(m)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = func(matrix[i][j])
    return matrix


def dot_matrix(m1, m2):
    if len(m1) == len(m2) and len(m1[0]) == len(m2):
        matrix = create_matrix(len(m1), len(m2[0]))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                sum = 0
                for k in range(len(m2)):
                    sum += m1[i][k] * m2[k][j]
                matrix[i][j] = sum
        return matrix
    else:
        print("dimension wrong")


def scale(m, n):
    matrix = copy_matrix(m)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = n * matrix[i][j]
    return matrix


def transpose(m):
    matrix = create_matrix(len(m), len(m[0]))
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[j][i] = m[i][j]
    return matrix
