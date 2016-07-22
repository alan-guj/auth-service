# -*- coding:utf-8 -*-
import consul

def consul_get_register_service(servicename,tag):
    myconsul = consul.Consul()

    try:
        servicesinfo=myconsul.catalog.service(service=servicename,tag=tag)
    except Exception as e:
        print("consul_get_register_service exception,get services exception,e=%s" % (e))
        return None

    if servicesinfo == None or len(servicesinfo) != 2:
        print("consul_get_register_service error,get services data error")
        return None

    #获取服务信息
    services=servicesinfo[1]
    servicesdict={}
    for service in services:
        serviceid=service['ServiceID']
        servicesdict[serviceid]=service

    #获取服务的健康状态
    try:
        healthsinfo=myconsul.health.checks(service=servicename)
    except Exception as e:
        print("consul_get_register_service exception,get healths exception,e=%s" % (e))
        return None

    if healthsinfo == None or len(healthsinfo) != 2:
        print("consul_get_register_service error,get healths data error")
        return None
    
    #加入健康状态
    healths=healthsinfo[1]
    for health in healths:
        serviceid=health['ServiceID']
        if serviceid not in servicesdict:
            continue
        else:
            servicesdict[serviceid]['Status']=health['Status']

    #返回值
    serviceslist=[]
    for key in servicesdict:
        if "Status" not in servicesdict[key]:
            servicesdict[key]['Status'] = "passing"
        serviceslist.append(servicesdict[key])

    return serviceslist

#注册服务
#返回值:
#True     --  ok
#other --  error
def consul_register_service(servicename,address,port,tag,healthcheckurl):
    myconsul = consul.Consul()
    check=consul.Check()
    
    serviceid=servicename + "_" + str(address) + "_" + str(port)
    servertags=[]
    servertags.append(tag)
    healthcheck=check.http(url=healthcheckurl,interval="15s")

    try:
        result=myconsul.agent.service.register(name=servicename,service_id=serviceid,address=address,port=port,tags=servertags,check=healthcheck)
    except Exception as e:
        print("consul_register_service exception,e=%s" % (e))
        return False

    if result != True:
        print("register_my_service_by_consul error,name=%s,id=%s,address=%s,port=%d,tag=%s,healthcheckurl=%s" %
                  (servicename,serviceid,address,port,tag,healthcheckurl))
        return False
    else:
        print("register_my_service_by_consul ok,name=%s,id=%s,address=%s,port=%d,tag=%s,healthcheckurl=%s" %
                  (servicename,serviceid,address,port,tag,healthcheckurl))
    return True