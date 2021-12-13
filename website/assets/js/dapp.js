// Requires jQuery
var address = "";
// 1. Defining dApp Connection
const detail = JSON.stringify({
    appName: 'Python USD dApp',
    version: '1.0.0',
    logo: 'logo.png',
    contractName: 'con_pyusd_v3',
    networkType: 'mainnet',
})

// 2. Wallet Event Listener
document.addEventListener('lamdenWalletInfo', (response) => {
    console.log(response);
    if(response.detail.errors !== undefined){
	    if(response.detail.errors[0] === "Wallet is Locked"){
	$("#connect_wallet").text("Unlock your Lamden Wallet first");}
    }
    if (response.detail.errors === undefined) {
        //Wallet is connected
        $("#connect_wallet").text("Connected");
        $("#address_span").removeClass("d-none");
        $("#game").removeClass("d-none");
        $("#game").addClass("d-block");
        $("#connect-first-game").addClass("d-none");
        $("#wallet_address").text(response.detail.wallets[0]);
        address = response.detail.wallets[0];
        var supply = 0;
        var reserve = 0;
        var exchange_rate = 0;
        //Refresh TAU Balance
        $.get(
            "https://masternode-01.lamden.io/contracts/currency/balances?key=" + address
        ).done(function (data__) {
            $("#tau_balance").html(
                Number(data__["value"]["__fixed__"]).toFixed(8)
            );
        });
        //Refresh PYUSD Balance
        $.get(
            "https://masternode-01.lamden.io/contracts/con_pyusd_v3/balances?key=" + address
        ).done(function (data__) {
            $("#pusd_balance").html(
                Number(data__["value"]["__fixed__"]).toFixed(8)
            );
        });
        //Refresh Ratio
        $.get(
            "https://masternode-01.lamden.io/contracts/con_rocketswap_official_v1_1/prices?key=con_lusd_lst001"
        ).done(function (data__) {
            exchange_rate = data__["value"]["__fixed__"];
            $("#exchange_rate").html(
                Number(exchange_rate).toLocaleString("en")
            );
            //Refresh Reserve
        $.get(
            "https://masternode-01.lamden.io/contracts/currency/balances?key=con_pyusd_v3"
        ).done(function (data__) {
            reserve = data__["value"]["__fixed__"];
            $("#reserve").html(
                Number(reserve).toLocaleString("en")
            );
            //Refresh Supply
            $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/total_supply"
            ).done(function (data__) {
                supply = data__["value"]["__fixed__"];
                $("#pusd_issued").html(
                    Number(supply).toLocaleString("en")
                );
                $("#backing_ratio").html(
                    Number((reserve * (1 / exchange_rate)) / supply).toLocaleString("en")
                );
            });
        
        });
        });
        
        
        return
    }
});

document.addEventListener('lamdenWalletTxStatus', (response) => 
	{
		if (response.detail.data.resultInfo.type === 'error' && response.detail.data.resultInfo.errorInfo[0] == 'Transaction nonce is invalid.') {
        console.log(response);
        toastr.error(response.detail.data.resultInfo.errorInfo[0], 'Error!')
        $("#swap").removeClass("disabled");
        $("#swap").text("Swap");
        return
    }
    if (response.detail.data.resultInfo.type === 'error' && response.detail.data.resultInfo.errorInfo[0] == 'Retry Attmpts 10 hit while checking for Tx Result.') {
        console.log(response);
        toastr.error(response.detail.data.resultInfo.errorInfo[0], 'Error!')
        $("#swap").removeClass("disabled");
        $("#swap").text("Swap");
        return
    }
    if (response.detail.data.resultInfo.title=="Transaction Successful" && response.detail.data.txInfo.methodName == "approve"){ 
        console.log(response);
        if($("#to").val() == "TAU"){
            const detail = JSON.stringify({
                contractName: 'con_pyusd_v3',
                methodName: 'pyusd_to_tau',
                networkType: 'mainnet',
                kwargs: {
                    amount: parseFloat($("#guess").val())
                    
                },
            
                stampLimit: 200,
            });
            document.dispatchEvent(new CustomEvent('lamdenWalletSendTx', {detail}));
            return
        }
        if($("#to").val() == "PUSD"){
            const detail = JSON.stringify({
                contractName: 'con_pyusd_v3',
                methodName: 'tau_to_pyusd',
                networkType: 'mainnet',
                kwargs: {
                    amount: parseFloat($("#guess").val())
                    
                },
            
                stampLimit: 200,
            });
            document.dispatchEvent(new CustomEvent('lamdenWalletSendTx', {detail}));
            return
        }
        
        
    }
    if (response.detail.data.resultInfo.title=="Transaction Successful" && response.detail.data.txInfo.methodName == "pyusd_to_tau" || response.detail.data.resultInfo.title=="Transaction Successful" && response.detail.data.txInfo.methodName == "tau_to_pyusd" ){
        console.log(response);
        var supply = 0;
        var reserve = 0;
        var exchange_rate = 0;
        //Refresh TAU Balance
        $.get(
            "https://masternode-01.lamden.io/contracts/currency/balances?key=" + address
        ).done(function (data__) {
            $("#tau_balance").html(
                Number(data__["value"]["__fixed__"]).toFixed(8)
            );
        });
        //Refresh PYUSD Balance
        $.get(
            "https://masternode-01.lamden.io/contracts/con_pyusd_v3/balances?key=" + address
        ).done(function (data__) {
            $("#pusd_balance").html(
                Number(data__["value"]["__fixed__"]).toFixed(8)
            );
        });
        //Refresh PYUSD Balance
        $.get(
            "https://masternode-01.lamden.io/contracts/con_pyusd_v3/balances?key=" + address
        ).done(function (data__) {
            $("#pusd_balance").html(
                Number(data__["value"]["__fixed__"]).toFixed(8)
            );
        });
        //Refresh Ratio
        $.get(
            "https://masternode-01.lamden.io/contracts/con_rocketswap_official_v1_1/prices?key=con_lusd_lst001"
        ).done(function (data__) {
            exchange_rate = data__["value"]["__fixed__"];
            $("#exchange_rate").html(
                Number(exchange_rate).toLocaleString("en")
            );
            //Refresh Reserve
        $.get(
            "https://masternode-01.lamden.io/contracts/currency/balances?key=con_pyusd_v3"
        ).done(function (data__) {
            reserve = data__["value"]["__fixed__"];
            $("#reserve").html(
                Number(reserve).toLocaleString("en")
            );
            //Refresh Supply
            $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/total_supply"
            ).done(function (data__) {
                supply = data__["value"]["__fixed__"];
                $("#pusd_issued").html(
                    Number(supply).toLocaleString("en")
                );
                $("#backing_ratio").html(
                    Number((reserve * (1 / exchange_rate)) / supply).toLocaleString("en")
                );
            });
        
        });
        });
        
        
         
        toastr.success('The swap was successful!', 'We are done!');
        
        
        $("#swap").removeClass("disabled");
        $("#swap").text("Swap");
        return
     } 
});

// 3. Dispatch Event on Page Load
$(document).ready(function () {
    document.dispatchEvent(new CustomEvent('lamdenWalletGetInfo'));
    $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/liquidity_tax"
            ).done(function (data__) {
                lp_fee = data__["value"];
                $("#fees_liquidity").html(
                    Number(lp_fee).toLocaleString("en") + " %"
                );
                
            });
    
    $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/dev_tax"
            ).done(function (data__) {
                dev_fee = data__["value"];
                $("#fees_dev").html(
                    Number(dev_fee).toLocaleString("en") + " %"
                );
                
            });
            $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/mint_tax"
            ).done(function (data__) {
                mint_fee = data__["value"];
                $("#fees_mint").html(
                    Number(mint_fee).toLocaleString("en") + " %"
                );
                
            });
   $.get(
            "https://masternode-01.lamden.io/contracts/con_rocketswap_official_v1_1/prices?key=con_lusd_lst001"
        ).done(function (data__) {
            exchange_rate = data__["value"]["__fixed__"];
           
        //Refresh Reserve
        $.get(
            "https://masternode-01.lamden.io/contracts/currency/balances?key=con_pyusd_v3"
        ).done(function (data__) {
            reserve = data__["value"]["__fixed__"];
            $("#transparency_locked").html(
                Number(reserve).toLocaleString("en") + " TAU"
            );
            //Refresh Supply
            $.get(
                "https://masternode-01.lamden.io/contracts/con_pyusd_v3/total_supply"
            ).done(function (data__) {
                supply = data__["value"]["__fixed__"];
                $("#transparency_supply").html(
                    Number(supply).toLocaleString("en") + " PUSD"
                );
                $("#transparency_br").html(
                    Number((reserve * (1 / exchange_rate)) / supply).toLocaleString("en")
                );
            });

        });
        }); 
});

// 4. Connect a Wallet Function
$("#connect_wallet").click(function () {
    console.log("Connect your wallet has been triggered.");
    document.dispatchEvent(new CustomEvent('lamdenWalletConnect', { detail }));
});

$( "#from" ).change(function() {
    if($("#from").val() == "TAU"){
        $("#to").val("PUSD");
        $("#bet_amount").val(Number($("#guess").val() / $("#exchange_rate").text()).toFixed(8));
    }
    if($("#from").val() == "PUSD"){
        $("#to").val("TAU");
        $("#bet_amount").val(Number($("#guess").val() * $("#exchange_rate").text()).toFixed(8));
    }
});
$( "#to" ).change(function() {
    if($("#to").val() == "TAU"){
        $("#from").val("PUSD");
        $("#bet_amount").val(Number($("#guess").val() * $("#exchange_rate").text()).toFixed(8));
    }
    if($("#to").val() == "PUSD"){
        $("#from").val("TAU");
        $("#bet_amount").val(Number($("#guess").val() / $("#exchange_rate").text()).toFixed(8));
    }
});

$( "#guess" ).keyup(function() {
    if($("#to").val() == "TAU"){
        $("#bet_amount").val(Number($("#guess").val() * $("#exchange_rate").text()).toFixed(8));
    }
    if($("#to").val() == "PUSD"){
        $("#bet_amount").val(Number($("#guess").val() / $("#exchange_rate").text()).toFixed(8));
    }
});

$( "#bet_amount" ).keyup(function() {
    if($("#to").val() == "TAU"){
        $("#guess").val(Number($("#bet_amount").val() / $("#exchange_rate").text()).toFixed(8));
    }
    if($("#to").val() == "PUSD"){
        $("#guess").val(Number($("#bet_amount").val() * $("#exchange_rate").text()).toFixed(8));
    }
});


// 5. Swap
$("#swap").click(function () {
    
    $("#swap").addClass("disabled");
    $("#swap").text("Swapping (Waiting for Transactions)..");
    if($("#to").val() == "TAU"){
        const detail = JSON.stringify({
            contractName: 'con_pyusd_v3',
            methodName: 'approve',
            networkType: 'mainnet',
            kwargs: {
                amount: parseFloat($("#guess").val()), 
                to: 'con_pyusd_v3'
            },
            stampLimit: 100,
        });
        document.dispatchEvent(new CustomEvent('lamdenWalletSendTx', {detail}));
    }
    if($("#to").val() == "PUSD"){
        const detail = JSON.stringify({
            contractName: 'currency',
            methodName: 'approve',
            networkType: 'mainnet',
            kwargs: {
                amount: parseFloat($("#guess").val()), 
                to: 'con_pyusd_v3'
            },
            stampLimit: 100,
        });
        document.dispatchEvent(new CustomEvent('lamdenWalletSendTx', {detail}));
    }
    
    

    
});
