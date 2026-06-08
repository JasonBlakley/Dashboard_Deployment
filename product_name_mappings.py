"""
Product Name Mapping Table
Maps ticket product names (as they appear in Cognos data) to lifecycle product names
(as they appear in IBM's lifecycle file).

This resolves the "blue bubble" issue where products show as "N/A Version" due to
name mismatches between ticket data and lifecycle dictionaries.

Last Updated: June 5, 2026
"""

# Product name mappings: ticket_name (lowercase) -> lifecycle_name (as it appears in lifecycle file)
PRODUCT_NAME_MAPPINGS = {
    # AIX Products
    "aix": "AIX Standard Edition",
    
    # Sterling Products (note: some use colon, some use space)
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
    
    # WebSphere Products
    "websphere": "IBM WebSphere Application Server",
    "websphere application server": "IBM WebSphere Application Server",
    "ibm websphere application server": "IBM WebSphere Application Server",
    
    # SPSS Products
    "spss modeler": "IBM SPSS Modeler",
    "spss statistics": "IBM SPSS Statistics",
    
    # Tivoli Products
    "tivoli monitoring agents": "IBM Tivoli Monitoring",
    "tivoli system automation application manager": "Tivoli System Automation Application Manager",
    
    # Red Hat Products
    "red hat enterprise linux server": "Red Hat Enterprise Linux Server",
    "red hat enterprise linux": "Red Hat Enterprise Linux Server",
    
    # IBM Cloud/Automation Products
    "urbancode deploy": "UrbanCode Deploy",
    "robotic process automation": "IBM Robotic Process Automation",
    
    # Security Products
    "security verify directory": "Security Verify Directory",
    
    # Storage Products
    "storage scale": "IBM Storage Scale",
    "spectrum scale": "IBM Storage Scale",  # Former name
    
    # Rational Products
    "rational licensing": "Rational License Key Server",
    
    # DB2 Products
    "db2": "IBM Db2",
    "db2 database": "IBM Db2",
    
    # MQ Products
    "mq": "IBM MQ",
    "ibm mq": "IBM MQ",
    "websphere mq": "IBM MQ",  # Former name
    
    # Cognos Products
    "cognos analytics": "IBM Cognos Analytics",
    "cognos": "IBM Cognos Analytics",
    
    # DataStage Products
    "datastage": "IBM InfoSphere DataStage",
    "infosphere datastage": "IBM InfoSphere DataStage",
    
    # Notes/Domino Products
    "notes": "IBM Notes",
    "domino": "IBM Domino",
    "lotus notes": "IBM Notes",  # Former name
    "lotus domino": "IBM Domino",  # Former name
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

# Made with Bob
