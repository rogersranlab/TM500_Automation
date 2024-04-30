import requests
import json
import os, time, json,platform,re
from datetime import datetime, timedelta

class class_TMA_API:

    """
    Author: Aaron.shi@rci.rogers.com
    This class is used to communicate TM500 via API 

    check_TMA_Status: verify TMA is on or off
        Arg: no
        return: response.status_code, response.text 

    open TMA: open TMA via API
        Arg: no
        return: response.status_code

    close TMA: close TMA via API
        Arg: no
        return: reponse.status_code, response.text

    check_TMA_location: verify TMA's location
        Arg: no
        return: response.status_code, response.text 

    schedule_campaign(self,campaignPath,testcaseNameList): schedule campaign by testcase list
        Arg: campaign path, list of test cases
        return: response.status_code, response.text     
    
    run_campaign(self)
        Arg: no
        return: response.status_code, response.text
    
    check_campaign_status(self):
        Arg: no
        return: response.status_code, response.text     

    stop_campaign(self):
        Arg: no
        return: response.status_code, response.text  

    generate_report(self):
        Arg: no
        return: response.status_code, response.text 
    
    check_report(self):
        Arg: no
        return: response.status_code, response.text 

    (600,0) is used to identify exception when running API call 
    """

    

    ################## Below are the constants for Testing ###################################
    baseURL = 'http://192.168.10.100:5099/rtc/v2/tmas'
    tmaType = '1'
    relativeURIe500 = '/0001/campaigns/actions/'
    tmaPath= ""
    campaignScheduled=""
    current_os=""
    ###########################################################################################

    def __init__(self):
        # Verify the operating system 
        self.current_os=self.detect_os() 
        self.tmaPath = "C:/'Program Files (x86)'/VIAVI/TM500/'5G NR - NLA 6.23.0'/'Test Mobile Application'"
        if self.current_os=="Linux":
            self.tmaPath = "C:/Program Files (x86)/VIAVI/TM500/5G NR - NLA 6.23.0/Test Mobile Application"
        print(self.tmaPath)


    def check_TMA_Status(self):
    # API to check TMA status when TMA is open
        url_instancecheck = self.baseURL
        try:
            response = requests.get(url_instancecheck, headers={"Content-Type":"application/json"})
            if response.status_code!=200:
                print(response.status_code,response.text)
                if response.text!="0001":
                    # if TMA status shows not open, try open it 
                    # For now, we are trying API call to TMA v6.23
                    openstatus=self.open_TMA()
                    if openstatus==201:
                        self.check_TMA_Status()
                    else:
                        return openstatus, response.text
            else:
                print("TMA status check API call successful")
            return response.status_code, response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception

    def open_TMA(self):
        # API to open TMA
        url_openTMA = self.baseURL
        jsonData = '{"TMA_TYPE":' + self.tmaType + ',"TMA_PATH":"' + self.tmaPath + '", "TMA_PROFILE": "Default User"}'
        print(jsonData)
        try:
            response = requests.post(url_openTMA,data=jsonData,headers={"Content-Type": "application/json"})
            time.sleep(10)
            if response.status_code!=201:
                print("TMA open API call failed!")
            else:
                print("TMA status check API call successful")
            return response.status_code
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception
        
    def close_TMA(self):
        # API to close TMA
        url_openTMA = self.baseURL
        try:
            response = requests.delete(url_openTMA,headers={"Content-Type": "application/json"})
            if response.status_code!=200:
                print("TMA close API call failed!")
            else:
                print("TMA close API call successful")
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception

    def check_TMA_location(self):
        #API to check TMA location
        url_location = self.baseURL + "/0001"
        try:
            response = requests.get(url_location, headers={"Content-Type":"application/json"})
            if response.status_code!=200:
                print("TMA location query API failed!")
                print(response.text)
            else:
                print("TMA location query API call successful")
                print("TMA location is:")
                print('\t'+response.text)
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception

    def schedule_campaign(self,campaignPath,testcaseNameList):
        # API to schedule by test case
        # campaignPath should be a XML path
        # testcaseName should be a list
        if not self.is_valid_xml_path(campaignPath):
            print("Please input a valid XML path")
            return 600,0
        elif not isinstance(testcaseNameList,list):
            print("Please input valid test case list")
            return 600,0
               
        url_location = self.baseURL + "/0001/campaigns/actions/schedule"
        jsonCampaign = '{"FILE_PATH": "' + campaignPath + '", "ITERATION_COUNT": 1,"ACTION_ON_EVENT": 2}'
        jsonCampaign_dict=json.loads(jsonCampaign)
        jsonTestcase={"TESTS_SELECTION_BY_NAME": testcaseNameList}
        jsonCampaign_dict.update(jsonTestcase)
        jsonCampaign=json.dumps(jsonCampaign_dict) # the complete json string 

        try:
            response = requests.post(url_location, data=jsonCampaign, headers={"Content-Type":"application/json"})
            if response.status_code!=200:
                print(response.text)
            else:
                print("Campaign scheduleing API call successful\n")
                print('\t'+response.text)
                self.campaignScheduled=response.text[1:]
            return response.status_code,response.text[1:]
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception
        
    def run_campaign(self):
        # API to run test case per scheduling
        if self.campaignScheduled=="":
            print("No campaign is scheduled!")
            return 600,0
             
        url_location = self.baseURL + "/0001/campaigns/actions/run"        
        jsonCampaignRun = '{"CAMPAIGN_NAME": "'+self.campaignScheduled + '","ADD_TO_ACTIVE_SCHEDULER": 1}'
        try:
            response = requests.post(url_location, data=jsonCampaignRun, headers={"Content-Type":"application/json"})
            if response.status_code!=200:
                print(response.text)
            else:
                print("Campaign running API call successful\n")
                print('\t'+response.text)
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception
    
    def check_campaign_status(self):
        # Check campaign status
        if self.campaignScheduled=="":
            print("No campaign is scheduled!")
            return 600,0
        
        url_location=self.baseURL+"/0001/campaigns/actions/run"
        # url_location="http://192.168.10.100:5099/rtc/v2/tmas/0001/campaigns/actions/run"
        try:
            response = requests.get(url_location, headers={"Content-Type":"application/json"})
            if response.status_code==200:
                print("TMA campaign status query API call successful!")
                print("Running campaign is:")
                print('\t'+response.text)
            elif response.status_code==404:
                print("No campaign is running")
                # self.campaignScheduled=""
            else:
                print("TMA campaign status call failed!")
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception
       
    def stop_campaign(self):
        # Stopping campaign
        if self.campaignScheduled=="":
            print("No campaign is scheduled!")
            return 600,0
        elif self.check_campaign_status!=200: # no campaign is running, no need to stop
            return 600,0
        
        url_location=self.baseURL+"/0001/campaigns/actions/stop"
        try:
            response = requests.get(url_location, headers={"Content-Type":"application/json"})
            if response.status_code!=200:
                print("TMA stop campaign API failed!")
            else:
                print("TMA stop campaign API call successful")
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception        

    def generate_report(self):
        # Report generation
        if self.campaignScheduled=="":
            print("No campaign is scheduled!")
            return 600,0
       
        url_location=self.baseURL+"/0001/campaigns/actions/generatereport"
        jsonReportGeneration = '{"CAMPAIGN_NAME": "'+self.campaignScheduled +'"}'
        try:
            response = requests.post(url_location, data=jsonReportGeneration,headers={"Content-Type":"application/json"})
            if response.status_code!=202:
                print("TMA report generation failed!")
            else:
                print("TMA report generation starts successful")
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception
        
    def check_report(self):
        # Report generation status check
        if self.campaignScheduled=="":
            print("No campaign is scheduled")
            return 600,0
        
        url_location=self.baseURL+"/0001/campaigns/actions/generatereport"
        try:
            response = requests.get(url_location,headers={"Content-Type":"application/json"})
            if response.status_code==200:
                print("TMA report is being generated!")
            elif response.status_code==404:
                print("TMA report generation starts successful")
            else:
                pass
            return response.status_code,response.text
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return 600,0 # use 600 to identify exception   

    # Other validatin functions
    def is_valid_xml_path(self,file_path):
        """
        Check if the given file path is a valid path to an XML file.
        
        Args:
            file_path (str): The file path to check.
            
        Returns:
            bool: True if the file path is valid, False otherwise.
        """
        if self.current_os=="Linux":
            linux_path=file_path.replace("\\","/")
            # Check if the path starts with "/mnt/c/" and remove it if necessary
            if linux_path.startswith("/mnt/c/"):
                linux_path = linux_path[len("/mnt/c/"):]
            linux_path=os.path.normpath(linux_path)
            if linux_path.lower().endswith('.xml'):
                return True
        elif self.current_os=="Windows":
            # Check if the path exists and points to a file
            if os.path.isfile(file_path):
            # Check if the file has an XML extension
                if file_path.lower().endswith('.xml'):
                    return True
            return False
        else:
            return False


    def detect_os(self):
        system = platform.system()
        if system == 'Windows':
            return 'Windows'
        elif system == 'Linux':
            return 'Linux'
        elif system == 'Darwin':
            return 'macOS'
        else:
            return 'Unknown'
        print(system)
    
    def path_catch(self,pathString):
        # Define a regular expression pattern to capture the path before "PASS"
        pattern = r'Complete\s+"([^"]+)"\s+"([^"]+)"\s+PASS'
        # Search for the pattern in the string
        match = re.search(pattern, pathString)
        if match:
        # Extract the path before "PASS"
            path_before_pass = match.group(2)
            print("Path found:", path_before_pass)
            return path_before_pass
        else:
            print("No match found.")
            return "No report path found"


if __name__ == "__main__":
    basictest=class_TMA_API()
    # Test 1: Perform end to end schedule=>Run=>generate report
    basictest.check_TMA_location()
    basictest.close_TMA()
    print(basictest.check_TMA_Status())
    basictest.stop_campaign()
    basictest.schedule_campaign("C:/TMA_Script/aaron_NSA - B7-N2.xml",['aaron_MultiSlice'])
    basictest.run_campaign()
    time.sleep(20)
    response_code,response_text=basictest.check_campaign_status()
    while response_text[-1]=='%':
        print("Test is still running!")
        print(response_text)
        time.sleep(5)
        response_code,response_text=basictest.check_campaign_status()
    basictest.generate_report()
    response_code,response_text=basictest.check_report()
    while response_text[-1]=='%':
        print("Report Generation is still running!")
        print(response_text)
        time.sleep(5)
        response_code,response_text=basictest.check_report()
    print(response_text)
    print(basictest.path_catch(response_text))
    # Test 2: Open TMA
    # basictest.open_TMA()
    
    





