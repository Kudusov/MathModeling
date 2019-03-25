from copy import deepcopy
from decimal import *
from prettytable import PrettyTable
from math import fabs
from numpy import finfo, float32

EPS = finfo(float32).eps

def some_feature():
    pass

def from_decimal_to_str(arr):
    result = list()
    for dec in arr:
        result.append('{:.7f}'.format(dec))
    return result


def from_decimal_to_str_decor(func):
    def wrapper(*args, **kwargs):
        return from_decimal_to_str(func(*args, **kwargs))

    return wrapper


class Term:
    def __init__(self, koef, power):
        """
        Лучше коеффициент хранить в виде числителя и знаменателя.
        Ну или придумать что-нибудь получше этого
        """
        self.koef = Decimal(koef)
        self.power = Decimal(power)

    def get_indefinite_integral(self):
        return Term(self.power + Decimal(1), self.koef / Decimal(self.power + 1))

    def calculate_indefinite_integral(self):
        self.power += Decimal(1)
        self.koef /= self.power

    def __mul__(self, other):
        return Term(self.koef * other.koef, self.power + other.power)

    def __add__(self, other):
        if self.power != other.power:
            return None

        return Term(self.koef + other.koef, self.power)

    def __str__(self):
        return str("{:.2g}".format(self.koef)) + " * p ^ " + str(self.power)


class Expression:
    terms = list()

    def __init__(self, lst):
        self.terms = deepcopy(lst)

    def __str__(self):
        return " + ".join(list(str(term) for term in self.terms))

    def set_expression(self, lst):
        self.terms = deepcopy(lst)

    def add_term(self, term):
        self.terms.append(term)

    def squaring(self):
        new_terms = list(term1 * term2 for term1 in self.terms for term2 in self.terms)
        self.terms = deepcopy(new_terms)

    def integrate(self):
        for term in self.terms:
            term.calculate_indefinite_integral()

    def group_by_powers(self):
        grouped_term = list()
        for i in range(len(self.terms)):
            for j in range(i + 1, len(self.terms)):
                if self.terms[i] is not None and self.terms[j] is not None and \
                                self.terms[i].power == self.terms[j].power:
                    self.terms[i] += self.terms[j]
                    self.terms[j] = None

            if self.terms[i] is not None:
                grouped_term.append(self.terms[i])

        self.terms = deepcopy(grouped_term)


class Pikar:
    def __init__(self, power):
        self.power = power
        self.expression = Expression(lst=None)
        self.expression = Expression([Term(koef=Decimal(1) / Decimal(3), power=Decimal(3))])

    def fill_expression(self):
        for _ in range(self.power - 1):
            self.expression.squaring()
            self.expression.add_term(Term(koef=1, power=2))
            self.expression.integrate()
            self.expression.group_by_powers()

    def fill_expression_without_grouping(self):
        for _ in range(self.power - 1):
            self.expression.squaring()
            self.expression.add_term(Term(koef=1, power=2))
            self.expression.integrate()

    def calculate_in_point(self, point):
        result = Decimal(0)
        for term in self.expression.terms:
            result += term.koef * (Decimal(point) ** term.power)
        return result

    @from_decimal_to_str_decor
    def calculate_in_interval(self, begin, end, step):
        result = list()
        begin += step
        while fabs(begin - EPS) <= end:
            result.append(self.calculate_in_point(begin))
            begin += step
        return result


def f(x, y):
    return x * x + y * y


@from_decimal_to_str_decor
def explicit_broken(begin, end, step):
    current_x = begin
    result = list()
    last_result = 0
    while fabs(current_x - EPS) <= end - step:
        last_result = last_result + step * f(current_x, last_result)
        result.append(last_result)
        current_x += step
    return result


@from_decimal_to_str_decor
def runge_kutta_2(begin, end, step):
    current_x = begin
    result = list()
    last_result = 0
    while fabs(current_x - EPS) <= end - step:
        f_current = f(current_x, last_result)
        last_result = last_result + step / 2 * (f_current + f(current_x + step, last_result + step * f_current))
        result.append(last_result)
        current_x += step
    return result


@from_decimal_to_str_decor
def runge_kutta_4(begin, end, step):
    current_x = begin
    result = list()
    last_result = 0
    while fabs(current_x - EPS) <= end - step:
        k1 = f(current_x, last_result)
        k2 = f(current_x + step / 2, last_result + step * k1 / 2)
        k3 = f(current_x + step / 2, last_result + step * k2 / 2)
        k4 = f(current_x + step, last_result + step * k3)

        last_result = last_result + step / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        result.append(last_result)
        current_x += step
    return result


if __name__ == '__main__':
    table_x = list()
    table = PrettyTable()
    pikar_begin, pikar_end = 3, 4
    print("Начало: 0")
    begin, end, step = 0, float(input("Конец: ")), float(input("Шаг: "))
    count = int((end - begin) / step)
    x_begin = begin
    for i in range(count):
        x_begin += step
        table_x.append(('{:.2f}'.format(x_begin)))


    table.add_column(fieldname="x", align='r', column=table_x)
    for i in range(pikar_begin, pikar_end):
        pikar = Pikar(power=i)
        pikar.fill_expression()
        table.add_column(fieldname="Пикар - " + str(i), align='r', column=pikar.calculate_in_interval(begin, end, step))
    table.add_column(fieldname="Ломанных", align='r', column=explicit_broken(begin, end, step))
    table.add_column(fieldname="Рунге-Кутта 2", align='r', column=runge_kutta_2(begin, end, step))
    table.add_column(fieldname="Рунге-Кутта 4", align='r', column=runge_kutta_4(begin, end, step))
    print(table)
