# Python USD - Experimental Risky Lamden Fully Decentralized Stable Coin

# Check collateralization TAU to PUSD by using get_current_backing_ratio()
# !! If it's 1 everything is fine and if > 1.5 it's amazing and overcollateralized !!

# You can exchange TAU to PUSD and PUSD to TAU at any point at the same ratio that LUSD-TAU is at using tau_to_pusd() or pusd_to_tau()
# Don't forget to approve TAU to con_pusd or tau_to_pusd() exchange function doesn't work or just use the Swap dApp UI
# Difference to LUSD is that PYUSD is collateralized by TAU on this chain instead of USDT

# No Slippage Stablecoin Swap available at https://pusd.to

import currency as tau

I = importlib

balances = Hash(default_value=0)
allowances = Hash(default_value=0)
metadata = Hash(default_value='')

dev_address = Variable()
total_supply = Variable()


@construct
def seed():
    metadata['token_name'] = "Python USD"
    metadata['token_symbol'] = "PUSD"
    metadata['dex'] = 'con_rocketswap_official_v1_1'
    metadata['lusd'] = 'con_lusd_lst001'

    metadata['dev_tax'] = 0.5
    metadata['mint_tax'] = 0.5
    metadata['liq_tax'] = 0.5

    metadata['operators'] = [
        'ae7d14d6d9b8443f881ba6244727b69b681010e782d4fe482dbfb0b6aca02d5d',
        '6a9004cbc570592c21879e5ee319c754b9b7bf0278878b1cc21ac87eed0ee38d'
    ]

    dev_address.set('pusd_devs')
    total_supply.set(0)

@export
def change_metadata(key: str, value: Any):
    assert key.lower() != 'operators', 'Can not change owners'
    assert value, 'Parameter "value" can not be empty'

    metadata[key][ctx.caller] = value

    owner1 = metadata['operators'][0]
    owner2 = metadata['operators'][1]

    if metadata[key][owner1] == metadata[key][owner2]:
        metadata[key] = value

        metadata[key][owner1] = ''
        metadata[key][owner2] = ''
    
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
    tax_amount = ((amount / lusd_price) / 100 * (metadata['dev_tax'] + metadata['liq_tax'] + metadata['mint_tax']))

    balances[ctx.caller] += ((amount / lusd_price) - tax_amount)
    balances[dev_address.get()] += tax_amount / 2 
    balances[ctx.this] += tax_amount / 2  # TODO: Check! 
    
    total_supply.set(total_supply.get() + (amount / lusd_price))

    if(tax_amount / 2 > 5):
        add_liquidity()

@export
def pusd_to_tau(amount: float):
    tax_amount = (amount / 100 * (metadata['dev_tax'] + metadata['liq_tax']))
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
def migrate_tau(contract: str, amount: float):
    approved_action('migrate_tau', contract, amount)

    tau.transfer(amount=amount, to=contract, main_account=ctx.this)
    assert_owner()

@export
def migrate_pusd(contract: str, amount: float):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[ctx.this] >= amount, 'Not enough coins to send!'

    approved_action('migrate_pusd', contract, amount)

    balances[ctx.this] -= amount
    balances[contract] += amount
    assert_owner()

@export
def migrate_lp(contract: str, amount: float):
    approved_action('migrate_lp', contract, amount)

    dex = I.import_module(metadata['dex'])
    dex.approve_liquidity(ctx.this, contract, amount)
    dex.transfer_liquidity(ctx.this, contract, amount)
    assert_owner()

@export
def withdraw_dev_funds(amount: float):
    assert amount > 0, 'Cannot send negative balances!'
    assert balances[dev_address.get()] >= amount, 'Not enough coins to send!'

    approved_action('withdraw_dev_funds', ctx.caller, amount)

    balances[dev_address.get()] -= amount
    balances[ctx.caller] += amount
    assert_owner()

def approved_action(action: str, contract: str, amount: float):
    owner1 = metadata['operators'][0]
    owner2 = metadata['operators'][1]

    assert metadata[action][owner1] = f'{contract}{amount}', f'Wrong metadata for {owner1}'
    assert metadata[action][owner2] = f'{contract}{amount}', f'Wrong metadata for {owner2}'

@export
def circulating_supply():
    return f'{total_supply.get() - balances[ctx.this]}'

@export
def total_supply():
    return f'{total_supply.get()}'

def assert_owner():
    assert ctx.caller in metadata['operators'], 'Only executable by operators!'
