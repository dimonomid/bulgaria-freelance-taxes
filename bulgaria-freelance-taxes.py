"""
This script generates a chart with the percentages to be paid in taxes and
other business-related expenses for freelancers in Bulgaria, when working as a
company or as an individual.

See full article for more details: https://dmitryfrank.com/articles/bulgaria_freelance_taxes

NOTE: it should be obvious, but just in case mentioning it explicitly: this
script generates very good estimations, but it's by no means 100% precise,
meaning, you can't rely on it for the actual accounting and tax reporting. The
intended use case for this script is to help you accurately estimate your taxes
if you're considering moving to Bulgaria to work there. When you actually move,
get yourself an accountant before you start working.
"""

import matplotlib.pyplot as plt
import numpy as np
import argparse

# Percentage which is taken as social security tax. There are 3 components:
# - State Social Insurance (in Bulgarian, ДОО):                     14.8%
# - Additional Mandatory Pension Insurance (in Bulgarian, ДЗПО):    5%
# - National Health Insurance Fund (in Bulgarian, НЗОК):            8%
#
# The first two are payable by everyone. The last one (health insurance) is
# only payable by EU citizens and those who have permanent residence permit.
# To get the actual percentage, use the soc_sec_factor function, which uses
# those constants and returns the total percentage based on the --citizen flag.
SOCIAL_SECURITY_FACTOR_MAIN = 0.148 + 0.05
SOCIAL_SECURITY_FACTOR_HEALTH = 0.08

# Income tax percentage, which is the same for companies and individuals.
INCOME_TAX_FACTOR = 0.10

# Dividend tax percentage. Obviously it's only relevant for companies.
DIVIDEND_TAX_FACTOR = 0.05

# Fixed percentage of the individual's gross income which the government
# "recognizes" as your expenses, regardless of your actual expenses.
RECOGNIZED_EXPENSES_INDIVIDUAL = 0.25

# Fixed business-related expenses which don't depend on the income. I include
# accountant fees here (150 BGN) plus bank fees for having two bank accounts
# (for an individual it's about 5 BGN, and for the company it's 15 BGN).

# Those numbers can of course vary depending on the accountant and the bank you
# choose, but those are definitely doable.
FIXED_EXPENSES_INDIVIDUAL = 150 + 5
FIXED_EXPENSES_COMPANY = 150 + 15

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# Required args
parser.add_argument('--socsec-base-min', help="Social Security base minimum, in BGN. In 2021, it was 650 BGN", type=int, required=True)
parser.add_argument('--socsec-base-max', help="Social Security base maximum, in BGN. In 2021, it was 3000 BGN", type=int, required=True)
parser.add_argument('--year', help="Year, just to include in the title", required=True)

# Optional args
parser.add_argument('--citizen', action='store_true', help="Having citizenship or permanent residence permit")
parser.add_argument('--gross-min', help="Min gross amount to chart", type=int, default=500)
parser.add_argument('--gross-max', help="Max gross amount to chart", type=int, default=25000)
parser.add_argument('--output', help="Output png filename", default="output.png")

args = parser.parse_args()

# Returns total social security factor, which depends on the --citizen flag.
def soc_sec_factor():
    if args.citizen:
        return SOCIAL_SECURITY_FACTOR_MAIN + SOCIAL_SECURITY_FACTOR_HEALTH

    return SOCIAL_SECURITY_FACTOR_MAIN

# Calculates net income for a company.
def get_net_company(gross):
    # First, calculate social security. Since it's all company's income, the
    # individual's income is zero, therefore the social security base is the
    # minimum.
    soc_sec = args.socsec_base_min * soc_sec_factor()

    # Calculate income tax base: gross income less expenses.
    income_tax_base = gross - FIXED_EXPENSES_COMPANY - soc_sec

    # Calculate income tax by just taking percentage from the tax base.
    income_tax = income_tax_base * INCOME_TAX_FACTOR

    # Calculate net income of the company, by deducting all expenses from the
    # gross income. Note that it's not the final number: what we're looking for
    # is the net income of the individual, not the company, so we also need to
    # deduct dividends tax as well.
    net_company = gross - soc_sec - income_tax - FIXED_EXPENSES_COMPANY

    # Finally, calculate net income of the individual, by deducting the
    # dividends tax.
    return net_company * (1.0 - DIVIDEND_TAX_FACTOR)

# Calculates net income for an individual.
def get_net_individual(gross):
    # First, calculate social security. Its base can be either the full gross
    # income, but it's capped as per args.socsec_base_max.
    soc_sec_base = gross
    if soc_sec_base > args.socsec_base_max:
        soc_sec_base = args.socsec_base_max

    soc_sec = soc_sec_base * soc_sec_factor()

    # Calculate income tax base: deduct the recognized expenses and social
    # security calculated above.
    income_tax_base = gross * (1.0 - RECOGNIZED_EXPENSES_INDIVIDUAL) - soc_sec

    # Calculate income tax by just taking percentage from the tax base.
    income_tax = income_tax_base * INCOME_TAX_FACTOR

    # Finally, calculate net income, by deducting all expenses from the gross income.
    return gross - soc_sec - income_tax - FIXED_EXPENSES_INDIVIDUAL

def plot_func(x):
    # Generate 100 datapoints
    x = np.linspace(x[0], x[1], 200)

    y_company    = list(map(lambda gross: 1 - get_net_company(gross)    / gross, x))
    y_individual = list(map(lambda gross: 1 - get_net_individual(gross) / gross, x))

    plt.title(f"Percentage of income to be paid in taxes and other expenses in {args.year},\n"
            f"if you {'HAVE' if args.citizen else 'DO NOT HAVE'} EU citizenship "
            "or permanent residence permit")

    plt.plot(x, y_company, label='Dividends from Company')
    plt.plot(x, y_individual, label='Individual')

    plt.legend()

plot_func(x=(args.gross_min, args.gross_max))

plt.axis([0, args.gross_max, 0, 0.5])

plt.grid(visible=True, which='major', color='k', linestyle='-')
plt.grid(visible=True, which='minor', color='r', linestyle='-', alpha=0.1)

ax = plt.gca()
ax.minorticks_on()
ax.set_xlabel('Monthly gross income in BGN')
ax.set_ylabel('Percentage of income to be paid in taxes etc')

# Make Y scale to be formatted as percentage
# TODO: right now there's a warning that "FixedFormatter should only be used
# together with FixedLocator", need to fix that.
current_values = ax.get_yticks()
ax.set_yticklabels(['{:,.0%}'.format(x) for x in current_values])

fig = plt.gcf()

fig.set_size_inches(7, 5)
fig.tight_layout()
fig.savefig(args.output, facecolor='w', edgecolor='w', pad_inches=0.1)
