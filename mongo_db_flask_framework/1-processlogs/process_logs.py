from tldextract import tldextract
from netaddr import valid_ipv4
import sys, datetime, dns.resolver, pyasn, geoip2.database, os, investigate, requests, json
from urllib2 import Request, urlopen

infile = sys.argv[1]
top_domains, temp_unique, category_lookup = [],[],[]
domains_outfile = 'processed/all_domains.txt'
subdomains_outfile = 'processed/all_subdomains.txt'
subdomains_not_in_top_1m = 'processed/subdomains_not_in_top_1m.txt'
domains_not_in_top_1m = 'processed/domains_not_in_top_1m.txt'
subdomains_in_top_1m = 'processed/subdomains_in_top_1m.txt'
domains_in_top_1m =  'processed/domains_in_top_1m.txt'
vt_inv_results_outfile = 'processed/vt_inv_results.txt'
asndb = pyasn.pyasn('../assets/build/ipasn_20170302.dat')
geoip2_reader = geoip2.database.Reader("../assets/build/GeoLite2-City.mmdb")

def write_file(line, filename):
    f = open(filename, 'a')
    f.write(line)
    f.write('\n')
    f.close()
        
with open('../assets/build/top-1m.csv','r') as td:
        for line in td:
            line = line.strip()
            line = line.split(',')
            top_domains.append(line[1])

def remove_files():
    if os.path.isfile(domains_outfile):
       os.remove(domains_outfile)
    if os.path.isfile(subdomains_outfile):
       os.remove(subdomains_outfile)
    if os.path.isfile(subdomains_not_in_top_1m):
       os.remove(subdomains_not_in_top_1m)
    if os.path.isfile(domains_not_in_top_1m):
       os.remove(domains_not_in_top_1m)
    if os.path.isfile(subdomains_in_top_1m):
       os.remove(subdomains_in_top_1m)
    if os.path.isfile(domains_in_top_1m):
       os.remove(domains_in_top_1m)
    if os.path.isfile(vt_inv_results_outfile):
       os.remove(vt_inv_results_outfile)

def get_asn_info(domain):
    try:
        A_record = dns.resolver.query(domain)
        for a in A_record:
            ip_address = str(a)
            asninfo = asndb.lookup(ip_address)
            asn_to_list = list(asninfo) #asninfo is a tuple. Convert to list.
            dnsdbasn = asn_to_list[0]
            dnsdbprefix = asn_to_list[1]
            if dnsdbasn == 36692:   #opendns ASN, replaces actual ASN when classified as malware by OpenDNS. 
                _ip, asn = inv_lookup(domain,'asn_ip')  # Lookup the real ASN from OpenDNS
                ip_address = str(_ip)
            else:
                asn = dnsdbasn    # Just the AS number
                #asn_prefix = asn_to_list[1] # Just the prefix
    except:
            asn, ip_address = 'NO-ASN', 'NO-IP'
    return domain,ip_address,asn

def vt_lookup(domain):
    categories,webutation,urls,unique_subdomains = [],[],[],[]
    with open('config/virustotal_token.txt') as API_KEY:
        api = API_KEY.read()
    parameters = {'domain': domain, 'apikey': api}
    response = requests.get('https://www.virustotal.com/vtapi/v2/domain/report', params=parameters)
    json_response = response.json()
    vt_categories = json_response['categories']
    threat_seeker_categories = json_response['Websense ThreatSeeker category']
    webutation_categories = json_response['Webutation domain info']
    detected_urls = json_response['detected_urls']
    resolutions = json_response['resolutions']
    subdomains = json_response['subdomains']
    categories.append(vt_categories[0])
    categories.append(threat_seeker_categories)
    webutation_safety_score = webutation_categories['Safety score']
    webutation_adult = webutation_categories['Adult content']
    webutation_verdict = webutation_categories['Verdict']
    webutation.append(webutation_safety_score)
    webutation.append(webutation_adult)
    webutation.append(webutation_verdict)
    for item in detected_urls:
        urls.append(item['url'])
    for sub in subdomains:
        if sub not in unique_subdomains:
            unique_subdomains.append(sub)
    return categories,webutation,urls,unique_subdomains

def inv_lookup(item,option):
    token = ()
    with open('config/investigate_token.txt') as API_KEY:
        token = API_KEY.read()
        token = token.rstrip()
    inv = investigate.Investigate(token)
    headers = {'Authorization': 'Bearer ' + token}
    
    if option == 'cat':
        res = inv.categorization(item, labels=True)
        inv_security_status = res[item]['status'] # Investigate maliciousness
        content_category = res[item]['content_categories'] # Investigate categorization
        if content_category == []:
                value = 'none'
                return value, inv_security_status
        else:
            for value in content_category:
                return value, inv_security_status

    if option == 'asn_ip':
        request = Request('https://investigate.api.opendns.com/dnsdb/name/a/' + item + '.json', headers=headers)
        response_body = urlopen(request).read()
        values = json.loads(response_body)
        ip = values['rrs_tf'][0]['rrs'][0]['rr']
        asn = values['features']['asns'][0]
        return ip, asn

def process_file():
    with open(infile, 'r') as f:
        for line in f:
            line = line.strip()
            line = line.replace('  ',' ')   # Some lines have double spaces. This gets rid of that.
            ls = line.split(' ')
            if len(ls) > 7:
                try:
                    domain = ls[5]
                    dateandtime = ('{0}:{1}:{2}'.format(ls[0],ls[1],ls[2]))
                    dt = datetime.datetime.strptime(dateandtime, '%b:%d:%H:%M:%S')
                    dt = dt.replace(year=2017) # year isn't specified, so I have to put it in
                    extracteddomain = tldextract.extract(domain)
                    firstlevel = extracteddomain.domain + '.' + extracteddomain.suffix
                    if extracteddomain.suffix =='':
                        continue
                    if extracteddomain.domain == '':
                        continue
                    else:
                        if firstlevel not in temp_unique: # Unique the time and domain so I don't get a bunch of repeats - lessens the bandwidth view, but speeds up processing time
                            print("Processing: {}".format(firstlevel))
                            invcategory_results = inv_lookup(firstlevel,'cat')
                            invcategory = str(invcategory_results[0])
                            invseccategory = invcategory_results[1]
                            if invcategory == 'none':
                                try:
                                    vt_results = vt_lookup(firstlevel)
                                    cat = vt_results[0][0]
                                    webutation = vt_results[1]
                                    urls = vt_results[2]
                                    unique_subdomains = vt_results[3]
                                except:
                                    cat = 'uncategorized'
                            else:
                                cat = invcategory

                            _asn_and_ip = get_asn_info(firstlevel)
                            asn_and_ip = list(_asn_and_ip)
                            asn, ip = asn_and_ip[2],asn_and_ip[1]
                            if valid_ipv4(ip):
                                try:
                                    geodata = geoip2_reader.city(ip) # get lat and lon
                                    latitude, longitude = geodata.location.latitude, geodata.location.longitude
                                except:
                                    latitude, longitude = 0,0
                            else:
                                latitude, longitude = 0,0
                            
                            #time_domain_ip = ("{},{},{}".format(dt,firstlevel, ip))
                            #time_sdomain_ip = ("{},{},{}".format(dt,domain, ip))
                            time_domain_ip = ("{}|{}|{}|{}|{}|{}|{}|{}|".format(dt,firstlevel,ip,asn,latitude, longitude,invseccategory,cat))
                            time_sdomain_ip = ("{}|{}|{}|{}|{}|{}|{}|{}|".format(dt,firstlevel,ip,asn,latitude, longitude,invseccategory,cat))
                            write_file(time_domain_ip,domains_outfile)
                            write_file(time_sdomain_ip,subdomains_outfile)

                            # VT and Investigate results all in one file:
                            time_domain_ip_all = ("{}|{}|{}|{}|{}|{}|{}|{}|".format(dt,firstlevel,ip,asn,latitude, longitude,invseccategory,cat))
                            if valid_ipv4(ip):
                                for i in webutation:
                                    time_domain_ip_all += str(i) + ','
                                time_domain_ip_all = time_domain_ip_all.rstrip(',')
                                time_domain_ip_all += "|"
                                for i in urls:
                                    time_domain_ip_all += str(i) + ','
                                time_domain_ip_all = time_domain_ip_all.rstrip(',')
                                time_domain_ip_all += "|"
                                for i in unique_subdomains:
                                    time_domain_ip_all += str(i) + ','
                                time_domain_ip_all = time_domain_ip_all.rstrip(',')
                                write_file(time_domain_ip_all.rstrip(','),vt_inv_results_outfile) 
                            else:
                                time_domain_ip_all += "||"
                                write_file(time_domain_ip_all,vt_inv_results_outfile) 
                            # Done with VT and Investigate results

                            if firstlevel not in top_domains:
                                write_file(time_sdomain_ip,subdomains_not_in_top_1m)
                                write_file(time_domain_ip,domains_not_in_top_1m)
                            if firstlevel in top_domains:
                                write_file(time_sdomain_ip,subdomains_in_top_1m)
                                write_file(time_domain_ip,domains_in_top_1m)
                            temp_unique.append(firstlevel)
                            
                except:
                    continue

remove_files()
process_file()