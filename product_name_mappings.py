"""
Product Name Mapping Table
Maps ticket product names (as they appear in Cognos data) to lifecycle product names
(as they appear in IBM's lifecycle file).

This resolves the "blue bubble" issue where products show as "N/A Version" due to
name mismatches between ticket data and lifecycle dictionaries.

IMPORTANT: All keys must be lowercase. Values should match the exact key in the
lifecycle dictionaries BEFORE they are lowercased (the lookup in calc_color will
lowercase the returned value for comparison).

Last Updated: June 8, 2026
"""

# Product name mappings: ticket_name (lowercase) -> lifecycle_name (as it appears in lifecycle file)
PRODUCT_NAME_MAPPINGS = {
    # AIX Products
    "aix": "AIX Standard Edition",

    # API Connect
    "api connect": "IBM API Connect",
    "ibm api connect": "IBM API Connect",

    # App Connect
    "app connect enterprise": "IBM App Connect Enterprise",
    "app connect professional": "IBM App Connect Professional",
    "ibm app connect enterprise": "IBM App Connect Enterprise",
    "ibm app connect professional": "IBM App Connect Professional",

    # Application Performance Analyzer
    "application performance analyzer": "IBM Application Performance Analyzer for z/OS",
    "application performance analyzer for z/os": "IBM Application Performance Analyzer for z/OS",

    # Apptio
    "apptio": "Apptio",

    # Big SQL
    "big sql": "IBM Big SQL",
    "ibm big sql": "IBM Big SQL",

    # Business Automation Workflow
    "business automation workflow": "IBM Business Automation Workflow",
    "ibm business automation workflow": "IBM Business Automation Workflow",

    # CICS
    "cics transaction server": "IBM CICS Transaction Server for z/OS",
    "cics transaction server for z/os": "IBM CICS Transaction Server for z/OS",

    # CL/SuperSession
    "cl/supersession": "IBM CL/SuperSession",

    # COBOL
    "cobol": "IBM Enterprise COBOL for z/OS",
    "enterprise cobol": "IBM Enterprise COBOL for z/OS",
    "enterprise cobol for z/os": "IBM Enterprise COBOL for z/OS",

    # Case Foundation
    "case foundation": "IBM Case Foundation",
    "ibm case foundation": "IBM Case Foundation",

    # Cloud Object Storage
    "cloud object storage": "IBM Cloud Object Storage System",
    "ibm cloud object storage": "IBM Cloud Object Storage System",

    # Cloud Pak for Business Automation
    "cloud pak for business automation": "IBM Cloud Pak for Business Automation",
    "ibm cloud pak for business automation": "IBM Cloud Pak for Business Automation",
    "cp4ba": "IBM Cloud Pak for Business Automation",

    # Cloud Pak for Data
    "cloud pak for data": "IBM Cloud Pak for Data",
    "ibm cloud pak for data": "IBM Cloud Pak for Data",
    "cp4d": "IBM Cloud Pak for Data",

    # Cloud Pak for Integration
    "cloud pak for integration": "IBM Cloud Pak for Integration",
    "ibm cloud pak for integration": "IBM Cloud Pak for Integration",
    "cp4i": "IBM Cloud Pak for Integration",

    # Cloudera
    "cloudera data platform data services with ibm": "Cloudera Data Platform Data Services with IBM",
    "cloudera data platform private cloud": "Cloudera CDP Private Cloud",
    "cloudera cdp private cloud": "Cloudera CDP Private Cloud",

    # Cognos
    "cognos analytics": "IBM Cognos Analytics",
    "cognos": "IBM Cognos Analytics",
    "ibm cognos analytics": "IBM Cognos Analytics",

    # Content Manager OnDemand
    "content manager ondemand": "Content Manager OnDemand",
    "ibm content manager ondemand": "Content Manager OnDemand",

    # Content Navigator
    "content navigator and content navigator mobile app": "IBM Content Navigator",
    "content navigator": "IBM Content Navigator",
    "ibm content navigator": "IBM Content Navigator",

    # Copy Services Manager
    "copy services manager": "IBM Copy Services Manager",
    "ibm copy services manager": "IBM Copy Services Manager",

    # Daeja ViewONE
    "daeja viewone": "IBM Daeja ViewONE",
    "ibm daeja viewone": "IBM Daeja ViewONE",

    # Data Studio
    "data studio": "IBM Data Studio",
    "ibm data studio": "IBM Data Studio",

    # DataPower
    "datapower": "IBM DataPower Gateway",
    "ibm datapower gateway": "IBM DataPower Gateway",
    "datapower gateway": "IBM DataPower Gateway",

    # Datacap
    "datacap": "IBM Datacap",
    "ibm datacap": "IBM Datacap",

    # Db2
    "db2": "IBM Db2",
    "db2 database": "IBM Db2",
    "ibm db2": "IBM Db2",
    "db2 connect": "IBM Db2 Connect",
    "ibm db2 connect": "IBM Db2 Connect",
    "db2 data management console": "IBM Db2 Data Management Console",
    "db2 linux, unix and windows": "IBM Db2",
    "db2 linux unix and windows": "IBM Db2",
    "db2 for z/os": "IBM Db2 for z/OS",
    "ibm db2 for z/os": "IBM Db2 for z/OS",

    # Debug for z/OS
    "debug for z/os": "IBM Debug for z/OS",
    "ibm debug for z/os": "IBM Debug for z/OS",

    # Dependency Based Build
    "dependency based build": "IBM Dependency Based Build",

    # DevOps Deploy (formerly UrbanCode Deploy)
    "devops deploy": "IBM DevOps Deploy",
    "ibm devops deploy": "IBM DevOps Deploy",
    "urbancode deploy": "IBM DevOps Deploy",
    "ibm urbancode deploy": "IBM DevOps Deploy",
    "ucd": "IBM DevOps Deploy",

    # Developer for z/OS
    "developer for z/os": "IBM Developer for z/OS",
    "ibm developer for z/os": "IBM Developer for z/OS",

    # Fault Analyzer
    "fault analyzer": "IBM Fault Analyzer for z/OS",
    "fault analyzer for z/os": "IBM Fault Analyzer for z/OS",

    # FileNet
    "filenet content manager": "IBM FileNet Content Manager",
    "ibm filenet content manager": "IBM FileNet Content Manager",
    "filenet image services": "IBM FileNet Image Services",
    "ibm filenet image services": "IBM FileNet Image Services",

    # FlashSystem
    "flashsystem 5100": "IBM FlashSystem 5100",
    "ibm flashsystem 5100": "IBM FlashSystem 5100",
    "flashsystem": "IBM FlashSystem",

    # GDPS
    "gdps (geographically dispersed parallel sysplex)": "IBM GDPS",
    "gdps": "IBM GDPS",

    # Guardium
    "guardium data encryption": "IBM Guardium Data Encryption",
    "ibm guardium data encryption": "IBM Guardium Data Encryption",
    "guardium data protection": "IBM Guardium Data Protection",
    "ibm guardium data protection": "IBM Guardium Data Protection",
    "guardium s-tap for z/os": "IBM Guardium S-TAP for z/OS",
    "ibm guardium s-tap for z/os": "IBM Guardium S-TAP for z/OS",

    # Hardware Management Console
    "hardware management console application": "IBM Hardware Management Console",
    "hardware management console": "IBM Hardware Management Console",

    # High Performance Unload
    "high performance unload": "IBM High Performance Unload for Db2 for z/OS",

    # Hortonworks
    "hortonworks data platform": "Hortonworks Data Platform",

    # Host Access Client Package
    "host access client package": "IBM Host Access Client Package",
    "ibm host access client package": "IBM Host Access Client Package",

    # IBM HTTP Server
    "ibm http server": "IBM HTTP Server",

    # IBM InfoSphere Information Server
    "ibm infosphere information server": "IBM InfoSphere Information Server",
    "infosphere information server": "IBM InfoSphere Information Server",

    # IBM Java
    "ibm java for z/os": "IBM SDK, Java Technology Edition",
    "ibm java": "IBM SDK, Java Technology Edition",

    # IBM Migration Utility
    "ibm migration utility": "IBM Migration Utility",

    # IBM i
    "ibm i": "IBM i",

    # IBM Log Cloud (placeholder - check exact lifecycle name)
    "ibm log cloud": "IBM Log Analysis",

    # MQ
    "mq": "IBM MQ",
    "ibm mq": "IBM MQ",
    "websphere mq": "IBM MQ",

    # Notes/Domino
    "notes": "IBM Notes",
    "domino": "IBM Domino",
    "lotus notes": "IBM Notes",
    "lotus domino": "IBM Domino",

    # Red Hat
    "red hat enterprise linux server": "Red Hat Enterprise Linux Server",
    "red hat enterprise linux": "Red Hat Enterprise Linux Server",

    # Robotic Process Automation
    "robotic process automation": "IBM Robotic Process Automation",
    "ibm robotic process automation": "IBM Robotic Process Automation",

    # Security Products
    "security verify directory": "Security Verify Directory",

    # SPSS
    "spss modeler": "IBM SPSS Modeler",
    "spss statistics": "IBM SPSS Statistics",

    # Sterling Products
    "sterling b2b integrator": "Sterling B2B Integrator",
    "sterling connect direct": "Sterling Connect:Direct",
    "sterling connect:direct": "Sterling Connect:Direct",
    "sterling connect direct for z/os": "Sterling Connect:Direct for z/OS",
    "sterling connect:direct for z/os": "Sterling Connect:Direct for z/OS",
    "sterling connect direct enterprise for z/os": "Sterling Connect:Direct Enterprise for z/OS",
    "sterling connect:direct enterprise for z/os": "Sterling Connect:Direct Enterprise for z/OS",
    "sterling file gateway": "Sterling File Gateway",
    "sterling gentran server": "Sterling Gentran Server",
    "sterling transformation extender": "Sterling Transformation Extender",
    "transformation extender advanced": "Transformation Extender Advanced",

    # Storage
    "storage scale": "IBM Storage Scale",
    "spectrum scale": "IBM Storage Scale",

    # Rational / License
    "rational licensing": "Rational License Key Server",

    # Tivoli
    "tivoli monitoring agents": "IBM Tivoli Monitoring",
    "tivoli system automation application manager": "Tivoli System Automation Application Manager",
    "tivoli netcool/omnibus": "Tivoli Netcool/OMNIbus",
    "netcool/omnibus": "Tivoli Netcool/OMNIbus",
    "tivoli netcool/impact": "Tivoli Netcool/Impact",
    "netcool/impact": "Tivoli Netcool/Impact",

    # WebSphere
    "websphere": "IBM WebSphere Application Server",
    "websphere application server": "IBM WebSphere Application Server",
    "ibm websphere application server": "IBM WebSphere Application Server",

    # DataStage
    "datastage": "IBM InfoSphere DataStage",
    "infosphere datastage": "IBM InfoSphere DataStage",
}


def get_mapped_product_name(product_name):
    """
    Get the lifecycle product name for a given ticket product name.

    Args:
        product_name (str): Product name from ticket data

    Returns:
        str: Mapped lifecycle product name, or original name if no mapping exists
    """
    if not product_name or not isinstance(product_name, str):
        return product_name

    product_lower = product_name.lower().strip()

    # Check for exact mapping
    if product_lower in PRODUCT_NAME_MAPPINGS:
        return PRODUCT_NAME_MAPPINGS[product_lower]

    # Return original if no mapping found
    return product_name


def normalize_version(version):
    """
    Normalize version strings to match lifecycle file formats.

    Common transformations:
    - "7.1 (EOS 4/30/2023)" -> "7.1.0", "7.1", "7.1.x"
    - "7.1" -> "7.1.0", "7.1", "7.1.x"
    - "9" -> "9.0"
    - "2021.1" -> "2021.1.0"

    Args:
        version (str): Version string from ticket data

    Returns:
        list: List of possible version formats to try matching
    """
    if not version or not isinstance(version, str):
        return [str(version).lower()]

    version = version.strip().lower()

    # Strip EOS dates like "(EOS 4/30/2023)" or "(eos 4/30/2017)"
    import re
    version = re.sub(r'\s*\(eos[^)]*\)', '', version, flags=re.IGNORECASE).strip()

    # Return list of possible version formats
    versions_to_try = [version]

    # If version doesn't end with .0, try adding it
    if '.' in version and not version.endswith('.0') and not version.endswith('.x'):
        versions_to_try.append(version + '.0')

    # If version has no dots, try adding .0
    if '.' not in version and version.replace('.', '').isdigit():
        versions_to_try.append(version + '.0')

    # If version ends with .0, try without it
    if version.endswith('.0'):
        versions_to_try.append(version[:-2])

    # Try with .x suffix (common in lifecycle file)
    if '.' in version and not version.endswith('.x'):
        parts = version.split('.')
        if len(parts) >= 2:
            versions_to_try.append(f"{parts[0]}.{parts[1]}.x")

    return versions_to_try
