# -*- coding:utf-8 -*-
import logging
import sys
from urllib.parse import urlparse
from sdk.consul_api import consul_get_register_service,consul_register_service
from config import WORK_ENV,CUSTOMER_CARE_SERVICE_NAME,MY_SERVICE_REGISTER,MY_SERVICE
from resources_json import other_services,customer_care_service_api_list

log = logging.getLogger('services_init')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

services = {}

#服务资源初始化
#返回值：
#True  -- ok
#False -- Error
def services_resources_init():
    global services

    #注册服务
    if MY_SERVICE_REGISTER:
        rc = service_register()
        if rc != True:
            log.debug("services_resources_init error,service_register error")
            return False

    #发现customer_care_service
    service=customer_care_service_find()
    if service == None:
        log.debug("services_resources_init error,customer_care_service_find error")
        return False

    serviceaddress=service['ServiceAddress']
    serviceport=service['ServicePort']

    #构造services
    for key in other_services:
        services[key]=other_services[key]
    for key in customer_care_service_api_list:
        services[key]= "http://" + str(serviceaddress) +":" + str(serviceport) + customer_care_service_api_list[key]

    return True

#发现customer_care_service
#返回值:
#None     --  error
#sservice -- ok
def customer_care_service_find():
    serviceslist=consul_get_register_service(CUSTOMER_CARE_SERVICE_NAME,WORK_ENV)
    if serviceslist == None or len(serviceslist) < 1:
        log.debug("customer_care_service_find error,consul_get_register_service error,servicename=%s,workenv=%s",CUSTOMER_CARE_SERVICE_NAME,WORK_ENV)
        return None

    #目前只取第一个，不支持集群及健康状态
    service=serviceslist[0]
    return service

#注册服务
#返回值：
#True   --  ok
#False  --  Error
def service_register():
    servicename = "customer_care_web_server"
    urlinfo = urlparse(MY_SERVICE)
    address = urlinfo.hostname
    if urlinfo.port == None:
        port = 80
    else:
        port = urlinfo.port
    tag = WORK_ENV
    healthcheckurl="http://" + address + ":" + str(port) + "/health/check"

    rc = consul_register_service(servicename,address,port,tag,healthcheckurl)
    if rc != True:
        log.debug("service_register error,consul_register_service error")
        return False

    return True

