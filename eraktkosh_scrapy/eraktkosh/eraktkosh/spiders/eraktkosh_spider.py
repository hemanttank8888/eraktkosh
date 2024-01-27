import re
import scrapy
import json

class EraktkoshSpiderSpider(scrapy.Spider):
    name = "eraktkosh_spider"
    allowed_domains = ["www.eraktkosh.in"]
    url = f"https://www.eraktkosh.in/BLDAHIMS/bloodbank/nearbyBB.cnt?hmode=GETSTATELIST"
    
    def start_requests(self):
        yield scrapy.Request(self.url,
                                method="GET",
                                headers={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
                                callback=self.parse,
                                dont_filter=True    
                                  )
    def parse(self, response):
        

        data = response.json()
        for state in data:
            state_value=state["value"]
            state_label=state["label"]
            state_path=f"https://www.eraktkosh.in/BLDAHIMS/bloodbank/nearbyBB.cnt?hmode=GETDISTRICTLIST&selectedStateCode={state_value}"
            yield scrapy.Request(state_path,
                        method="GET",
                        headers={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
                        meta={"state_value":state_value,"state_label":state_label},
                        callback=self.parse_district,
                        dont_filter=True    
                        )
    def parse_district(self, response):
        
        state_value=response.meta["state_value"]
        state_label=response.meta["state_label"]
        district_json = response.json()
        district_list=district_json['records']
        blood_groups=['18', '17', '12', '11', '14', '13', '23', '22', '16', '15']
        blood_components=['11', '14', '18', '28', '23', '24', '16', '15', '20', '19', '12', '30', '29', '13', '17', '21']

        for state in district_list:
            district_value=state["value"]
            district_name=state["id"]
            for blood_group in blood_groups:
                for blood_component in blood_components:
                    get_data_path=f"https://www.eraktkosh.in/BLDAHIMS/bloodbank/nearbyBB.cnt?hmode=GETNEARBYSTOCKDETAILS&stateCode={state_value}&districtCode={district_value}&bloodGroup={blood_group}&bloodComponent={blood_component}"
                    yield scrapy.Request(get_data_path,
                                method="GET",
                                headers={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'},
                                meta={"get_data_path":get_data_path,"state_label":state_label,"district_name":district_name},
                                callback=self.parse_get_data,
                                dont_filter=True    
                                )
    
    def parse_get_data(self, response):
        data = response.json()
        get_data_path=response.meta['get_data_path']
        state_label=response.meta['state_label']
        district_name=response.meta['district_name']
        datas=data["data"]
        if datas:
            for s_no in datas:
                try:
                    stat_name=state_label
                except:
                    stat_name=None
                try:
                    district=district_name
                except:
                    district=None
                try:
                    s_number=s_no[0]
                except:
                    s_number=None
                try:

                    email_list=s_no[1].split(",")
                    if "Email:" in email_list[-1]:
                        email=email_list[-1].replace("Email:","").replace("\n","").replace("\t","").replace(" ","")
                except:
                    email=None
                try:
                    listo=s_no[1].split("Fax:")
                    lists=listo[1].split("Email:")
                    fax=lists[0]
                    # print(fax)
                    # list=s_no[1].replace("-","").replace(" ","").replace("\n","").replace("\t","")
                    # Fax_list=list.split(",")
                    # if "Fax:" in email_list[-2]:
                    #     fax=Fax_list[-2].replace("Fax:","").replace("-","").replace("\n","").replace("\t","").replace(" ","")
                except:
                    fax=None
                try:
                    # list=s_no[1].replace("-","").replace(" ","").replace("\n","").replace("\t","")
                    list=s_no[1].split("Phone:")
                    phone1=list[1].split("Fax:")
                    Phone_no=phone1[0]
                    
                except:
                    Phone_no=None
                try:
                    namelist=s_no[1].split(",")
                    address=namelist[0:-2]
                    Blood_Bank_address = ''.join([re.sub(r'\d+', '', string) for string in address]).replace("Phone:","").replace("<br/>"," ")
                except:
                    Blood_Bank_address=None
                try:
                    catagory=s_no[2]
                except:
                    catagory=None
                try:
                    availability=s_no[3].replace("<p class='text-danger'><b>","").replace("<p class='text-success'>","").replace("</p>","").replace("</b>","")
                except:
                    availability=None
                try:
                    last_update=s_no[4]
                except:
                    last_update=None
                try:
                    type=s_no[5]
                except:
                    type=None
                yield {             
                        "s_number":s_number,
                        "Blood_Bank_address":Blood_Bank_address,
                        "state":stat_name,
                        "district":district,
                        "Phone_no":Phone_no,
                        "Fax":fax,
                        "Email":email,
                        "catagory":catagory,
                        "availability":availability,
                        "last_update":last_update,
                        "type":type
                }
            