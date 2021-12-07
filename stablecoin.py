# Python USD - Experimental Risky Lamden Fully Decentralized Stable Coin
# Check collateralization TAU to PYUSD by using get_current_backing_ratio()
# !!If its 1 everything is fine and > 1.5 its amazing and overcollateralized!!
# You can exchange TAU to PYUSD and PYUSD to TAU at any point at the same ratio that LUSD-TAU is at using tau_to_pyusd() or pyusd_to_tau()
# Dont forget to approve TAU to con_pyusd or tau_to_pyusd() exchange function doesnt work or just use the Swap dApp UI
# Difference to LUSD is that PYUSD is collateralized by TAU on this chain instead of USDT
# 2% protocol fee only on tau_to_pyusd() or pyusd_to_tau() - no extra fee on rocketswap but limited liq on rocketswap
# No Slippage Stablecoin Swap available at TODO: insert link here !!!

import currency as tau
import con_rocketswap_official_v1_1 as rocketswap

balances = Hash(default_value=0)
metadata = Hash()


prices = ForeignHash(foreign_contract='con_rocketswap_official_v1_1', foreign_name='prices')

dev_tax = Variable()
liquidity_tax = Variable()

dev_address = Variable()
total_supply = Variable()


@construct
def seed():
    metadata['token_name'] = "Python USD"
    metadata['token_symbol'] = "PUSD"
    metadata['operator'] = ctx.caller

    balances[ctx.caller] = 0

    dev_tax.set(1)
    dev_address.set('6a9004cbc570592c21879e5ee319c754b9b7bf0278878b1cc21ac87eed0ee38d')
    liquidity_tax.set(1)
    
    total_supply.set(0)

@export
def change_metadata(key: str, value: Any):
    assert ctx.caller == metadata['operator'], 'Only operator can set metadata!'
    metadata[key] = value

@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.caller] >= amount, 'Not enough coins to send!'
    balances[ctx.caller] -= amount
    balances[to] += amount

@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'
    balances[ctx.caller, to] += amount

@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[main_account, ctx.caller] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, ctx.caller], amount)
    assert balances[main_account] >= amount, 'Not enough coins to send!'
    balances[main_account, ctx.caller] -= amount
    balances[main_account] -= amount
    balances[to] += amount

@export
def tau_to_pyusd(amount: float): 
    tau.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)
    tax_amount = ((amount / prices["con_lusd_lst001"]) / 100 * (dev_tax.get() + liquidity_tax.get()))
    balances[ctx.caller] += ((amount / prices["con_lusd_lst001"]) - tax_amount)
    balances[dev_address.get()] += tax_amount / 2 
    balances[ctx.this] += tax_amount / 2 
    total_supply.set(total_supply.get() + (amount / prices["con_lusd_lst001"])) 
    if(tax_amount/2 > 5):
        add_liquidity()

@export
def pyusd_to_tau(amount: float): 
    tax_amount = (amount / 100 * (dev_tax.get() + liquidity_tax.get()))
    final_amount = amount - tax_amount
    balances[ctx.caller] -= amount
    balances[dev_address.get()] += tax_amount / 2 
    balances[ctx.this] += tax_amount / 2 
    total_supply.set(total_supply.get() - final_amount) 
    tau.transfer(amount=final_amount*prices["con_lusd_lst001"], to=ctx.caller)
    if(tax_amount/2 > 5):
        add_liquidity()

@export
def get_current_backing_ratio():
    # > 1 = Good
    return ((tau.balance_of(ctx.this) * (1 / prices["con_lusd_lst001"])) / circulating_supply())


def add_liquidity():
    token_amount = balances[ctx.this]
    approve(amount=token_amount, to="con_rocketswap_official_v1_1")
    tau_amount = rocketswap.sell(contract=ctx.this, token_amount=token_amount/2)
    tau.approve(amount=tau_amount, to="con_rocketswap_official_v1_1")
    rocketswap.add_liquidity(contract=ctx.this, currency_amount=tau_amount)


@export
def emergency_backing_add(amount: float):
    assert ctx.caller == metadata['operator'], 'Only operator can add emergency backing!'
    tau.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

@export
def circulating_supply():
    return (total_supply.get() - balances[ctx.this])

@export
def total_supply():
    return (total_supply.get())
