from wdmmg.lib import calculator

def test_tax_share():
    ans = calculator.tax_share(30000, 12000, True, True)
    assert 3000<ans<15000, ans

def test_spending_share():
    test_tax = 5000
    ans = calculator.spending_share(test_tax)
    assert 'health' in ans
    assert abs(sum(ans.values()) - test_tax) < 0.01

