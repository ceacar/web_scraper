port=${PORT:?port not set}
echo $port

#url_md5=$(echo "http://www.google.com"|md5sum|cut -d ' ' -f 1)
#echo "$url_md5"
curl -i --write-out %{http_code} --header "Content-Type: application/json" \
    --request POST \
        --data "{\"url\":\"https://www.amazon.com/Seagate-ST1000NM0033-Enterprise-Storage-7200RPM/dp/B00BVW6MEO\", \"ids\":[{\"identifier\":\"span\",\"id\":\"productTitle\"}, {\"identifier\":\"span\",\"id\":\"priceblock_ourprice\"}]}" \
    http://localhost:$port/scrap

        #--data "{\"url\":\"https://www.amazon.com/Seagate-ST1000NM0033-Enterprise-Storage-7200RPM/dp/B00BVW6MEO\", \"ids\":\"[{\"identifier\":\"span\",\"id\":\"productTitle\"},{\"identifier\":\"span\", \"id\":\"priceblock_ourprice\"}]\"}" \
#save with key and value
#curl -i --write-out %{http_code} --header "Content-Type: application/json" \
#    --request POST \
#    --data "{\"key\":\"$url_md5\", \"value\": \"00432a3bfe0a75e2dd886f7df2f85701\"}" \
#    http://localhost:$port/save
echo
echo
#get with key
#curl -i --write-out %{http_code} http://localhost:$port/get/$url_md5
echo

