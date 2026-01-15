import sympy as sp


def per_capita_growth_rate(n0, n1, years):
    return sp.log(n1 / n0) / years


def doubling_time(r):
    return sp.log(2) / r


# 1) Year 600: 200 million; year 1300: 360 million
r_600_1300 = per_capita_growth_rate(200, 360, 1300 - 600)

# 2) Doubling time based on the same data:
dt_600_1300 = doubling_time(r_600_1300)


# 3) Year 1000: 265 million; year 1200: 360 million.
r_1000_1200 = per_capita_growth_rate(265, 360, 1200 - 1000)
years_to_1975 = 1975 - 1000
prediction_1975 = 265 * sp.exp(r_1000_1200 * years_to_1975)

print(f"Prediction for 1975: {prediction_1975:.2f} million")


# 4) Doubling time using data after year 1650:
# Year 1750: 720 million; year 1850: 1200 million.
r_1750_1850 = per_capita_growth_rate(720, 1200, 1850 - 1750)
dt_1750_1850 = doubling_time(r_1750_1850)

# 5) Comparison question:
# The growth rate cannot be assumed to be constant. Historically, the rates have varied significantly in different periods.

