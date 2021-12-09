# Python USD - Experimental Risky Lamden Fully Decentralized Stable Coin
# Check collateralization TAU to PYUSD by using get_current_backing_ratio()
# !!If its 1 everything is fine and > 1.5 its amazing and overcollateralized!!
# You can exchange TAU to PYUSD and PYUSD to TAU at any point at the same ratio that LUSD-TAU is at using tau_to_pyusd() or pyusd_to_tau()
# Dont forget to approve TAU to con_pyusd or tau_to_pyusd() exchange function doesnt work or just use the Swap dApp UI
# Difference to LUSD is that PYUSD is collateralized by TAU on this chain instead of USDT
# 2% protocol fee only on tau_to_pyusd() or pyusd_to_tau() - no extra fee on rocketswap but limited liq on rocketswap
# No Slippage Stablecoin Swap available at TODO: insert link here !!!

import currency as tau

I = importlib

balances = Hash(default_value=0)
allowances = Hash(default_value=0)

metadata = Hash()

dev_tax = Variable()
liquidity_tax = Variable()
dev_address = Variable()
total_supply = Variable()


@construct
def seed():
    metadata['token_name'] = "Python USD"
    metadata['token_symbol'] = "PUSD"
    metadata['operator'] = ctx.caller
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    metadata['lusd'] = 'con_lusd_lst001'

    dev_tax.set(1)
    liquidity_tax.set(1)
    dev_address.set('pusd_devs')
    
    total_supply.set(0)

@export
def change_metadata(key: str, value: Any):
    metadata[key] = value
    assert_owner()

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'

    balances[ctx.caller] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    
    allowances[ctx.caller, to] += amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert allowances[main_account, ctx.caller] >= amount, f'You approved {allowances[main_account, ctx.caller]} but need {amount}'
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    
    allowances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += amount

@export
def tau_to_pusd(amount: float): 
    tau.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

    prices = ForeignHash(foreign_contract=metadata['dex'], foreign_name='prices')

    lusd_price = prices[metadata['lusd']]
    tax_amount = ((amount / lusd_price) / 100 * (dev_tax.get() + liquidity_tax.get()))

    balances[ctx.caller] += ((amount / lusd_price) - tax_amount)
    balances[dev_address.get()] += tax_amount / 2 
    balances[ctx.this] += tax_amount / 2 
    
    total_supply.set(total_supply.get() + (amount / lusd_price))

    if(tax_amount / 2 > 5):
        add_liquidity()

@export
def pusd_to_tau(amount: float):
    tax_amount = (amount / 100 * (dev_tax.get() + liquidity_tax.get()))
    final_amount = amount - tax_amount

    prices = ForeignHash(foreign_contract=metadata['dex'], foreign_name='prices')

    tau.transfer(amount=final_amount * prices["con_lusd_lst001"], to=ctx.caller)
    
    balances[ctx.caller] -= amount
    balances[dev_address.get()] += tax_amount / 2 
    balances[ctx.this] += tax_amount / 2 
    
    total_supply.set(total_supply.get() - final_amount)

    if(tax_amount / 2 > 5):
        add_liquidity()

@export
def get_current_backing_ratio():  # > 1 = Good
    prices = ForeignHash(foreign_contract=metadata['dex'], foreign_name='prices')
    return ((tau.balance_of(ctx.this) * (1 / prices[metadata['lusd']])) / circulating_supply())

def add_liquidity():
    approve(amount=balances[ctx.this], to=metadata['dex'])
    tau_amount = I.import_module(metadata['dex']).sell(contract=ctx.this, token_amount=balances[ctx.this] / 2)

    tau.approve(amount=tau_amount, to=metadata['dex'])
    I.import_module(metadata['dex']).add_liquidity(contract=ctx.this, currency_amount=tau_amount)

@export
def emergency_withdraw_tau(amount: float):
    tau.transfer(amount=amount, to=ctx.caller, main_account=ctx.this)
    assert_owner()

@export
def emergency_withdraw_pusd(amount: float):
    assert amount > 0, 'Cannot send negative balances!'

    balances[ctx.this] -= amount
    balances[ctx.caller] += amount

    assert_owner()

@export
def withdraw_dev_funds(amount: float):
    assert amount > 0, 'Cannot send negative balances!'

    balances[dev_address.get()] -= amount
    balances[ctx.caller] += amount

    assert_owner()

@export
def circulating_supply():
    return f'{total_supply.get() - balances[ctx.this]}'

@export
def total_supply():
    return f'{total_supply.get()}'

def assert_owner():
    assert ctx.caller == metadata['operator'], 'Only executable by operators!'
