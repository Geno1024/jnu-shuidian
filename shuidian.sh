#crypt() { node -e "var CryptoJS = require(\"crypto-js\"); console.log(CryptoJS.AES."$1"crypt('$2', CryptoJS.enc.Hex.parse(\"436574536f667445454d537973576562\"), {iv: CryptoJS.enc.Hex.parse(\"1934577290ABCDEF1264147890ACAE45\")}).toString())"; }
#decrypt() { crypt de $1; }
#encrypt() { crypt en $1; }

decrypt() { node -e "var CryptoJS = require(\"crypto-js\"); console.log(CryptoJS.AES.decrypt('$1', CryptoJS.enc.Hex.parse(\"436574536f667445454d537973576562\"), {iv: CryptoJS.enc.Hex.parse(\"1934577290ABCDEF1264147890ACAE45\")}).toString())"; }

encrypt() { node -e "var CryptoJS = require(\"crypto-js\"); console.log(CryptoJS.AES.encrypt('$1', CryptoJS.enc.Hex.parse(\"436574536f667445454d537973576562\"), {iv: CryptoJS.enc.Hex.parse(\"1934577290ABCDEF1264147890ACAE45\")}).toString())"; }


getCookie()
{
    curl -se "http://10.136.2.5/JNUWeb/" -H "Content-Type: application/json" -d "{\"nodeType\":0,\"nodeID\":0}" "http://10.136.2.5/JNUWeb/webservice/JNUService.asmx/GetEnergyTypeInfo" -c - | grep -Po "(?<=ASP.NET_SessionId\t)\S+"
}

session=$(getCookie)

getCustomerId()
{
    curl -se "http://10.136.2.5/JNUWeb/" -d "{\"user\":\"$1\",\"password\":\"2ay/7lGoIrXLc9KeacM7sg==\"}" -b "ASP.NET_SessionId=$session" -H "Content-Type: application/json" http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/Login | grep -Po "(?<=customerId\":)\d+"
}

getDate() { date +"%Y-%m-%d %H:%M:%S"; }

getInfo()
{
    room=$2
    time=$(getDate)
    userId=$(getCustomerId $room)
    cookie="ASP.NET_SessionId=$session; jnu-lp=$(encrypt $room)"
    token=$(encrypt "{\"userID\":$userId,\"tokenTime\":\"$time\"}")
echo $token
    curl -e "http://10.136.2.5/JNUWeb/" -H "Content-Type: application/json; charset=UTF-8" -H "DateTime: $time" -H "X-Requested-With: XMLHttpRequest" -H "Token: $token" -H "Connection: keep-alive" -H "Content-Length: 0" -b "$cookie" -X POST http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/$1
}

getInfoWithData()
{
    room=$2
    time=$(getDate)
    userId=$(getCustomerId $room)
    cookie="ASP.NET_SessionId=$session; jnu-lp=$(encrypt $room)"
    token=$(encrypt "{\"userID\":$userId,\"tokenTime\":\"$time\"}")
    curl -e "http://10.136.2.5/JNUWeb/" -H "Content-Type: application/json; charset=UTF-8" -H "DateTime: $time" -H "X-Requested-With: XMLHttpRequest" -H "Token: $token" -H "Connection: keep-alive" -b "$cookie" -d "$3" http://10.136.2.5/JNUWeb/WebService/JNUService.asmx/$1
}

getAccountBalance() { getInfo GetAccountBalance $1; }

getUserInfo() { getInfo GetUserInfo $1; }

getBillCost() { getInfoWithData GetBillCost $1 $2; } # {"energyType":0,"startDate":"2017-09-01","endDate":"2017-10-01"}

getSubsidy() { getInfoWithData GetSubSidy $1 $2; } # {"startDate":"2017-09-01","endDate":"2017-10-01"}

getCustomerMetricalData() { getInfoWithData GetCustomerMetricalData $1 $2; } # {"energyType":0,"startDate":"2017-09-01","endDate":"2017-10-01","interval":1} {"energyType":0,"startDate":"2017-01-01","endDate":"2018-01-01","interval":3}

getPaymentRecord() { getInfoWithData GetPaymentRecord$1 $2 $3; } # {"startIdx":0,"recordCount":10}


room=$1
# usage
getAccountBalance $room
echo ""
getUserInfo $room
echo ""
getBillCost $room "{\"energyType\":0,\"startDate\":\"2017-09-01\",\"endDate\":\"2017-10-01\"}"
echo "" 
getSubsidy $room "{\"startDate\":\"2017-09-01\",\"endDate\":\"2017-10-01\"}"
echo ""
getCustomerMetricalData $room "{\"energyType\":0,\"startDate\":\"2017-09-01\",\"endDate\":\"2017-10-01\",\"interval\":1}"
echo ""
getCustomerMetricalData $room "{\"energyType\":0,\"startDate\":\"2017-01-01\",\"endDate\":\"2018-10-01\",\"interval\":3}"
getPaymentRecord "?_dc=$(date +%s)" $room "{\"startIdx\":0,\"recordCount\":10}"
