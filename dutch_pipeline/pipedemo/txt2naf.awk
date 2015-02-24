BEGIN { monthnum["Jan"] = "01"
        monthnum["Feb"] = "02"
        monthnum["Mar"] = "03"
        monthnum["Apr"] = "04"
        monthnum["May"] = "05"
        monthnum["Jun"] = "06"
        monthnum["Jul"] = "07"
        monthnum["Aug"] = "08"
        monthnum["Sep"] = "09"
        monthnum["Oct"] = "10"
        monthnum["Nov"] = "11"
        monthnum["Dec"] = "12"
}

NR==1 {title=$0}
NR==2 {oridate=$0}
NR==3 {text = $0}
NR>3 {
#  gsub(" ,", ","); gsub(" .", "."); gsub("( ", "("); gsub(" )", ")");
       text=text "\n" $0
     }

END {
    printf("<NAF xml:lang=\"nl\" version=\"v3\">\n")
    printf("  <nafHeader>\n")
    printf("    <fileDesc creationtime=\"" finaldate(oridate) "\" title=\"" title "\" />\n")
    printf("  </nafHeader>\n")
    printf("  <raw><![CDATA[%s]]></raw>\n", text)
    printf("</NAF>\n")
}


function finaldate(oridate) {
    split(oridate, datelems, "-")
    day = datelems[1]
    year = 2000 + datelems[3]
    month = monthnum[datelems[2]]
    return year "-" month "-" day "T00:00:00Z"
    }
