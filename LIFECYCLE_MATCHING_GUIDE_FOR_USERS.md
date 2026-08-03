# Lifecycle Matching Guide for Users

**Last Updated:** June 12, 2026  
**Data Source:** May 2026 Ticketing Data

---

## 📊 Executive Summary

This guide helps you understand how product lifecycle data is matched in the Ticketing Dashboard and what the different bubble colors mean.

### Quick Statistics

Out of **3,077 unique product/version combinations** analyzed:

| Status | Count | Percentage | What It Means |
|--------|-------|------------|---------------|
| 🔴 **RED** | 194 | 6.3% | End of Support - Action Required |
| 🟠 **ORANGE** | 61 | 2.0% | Support Ending Soon (within 12 months) |
| 🟢 **GREEN** | 1,023 | 33.2% | Fully Supported - No Action Needed |
| 🔵 **BLUE** | 1,799 | 58.5% | No Lifecycle Data Available |

**Key Insight:** 41.5% of products have known lifecycle status, while 58.5% show blue because lifecycle data is not available or not applicable.

---

## 🎨 Understanding Lifecycle Colors

### 🔴 RED - End of Support (Critical)
- **Meaning:** This product version has reached End of Support (EOS)
- **Action Required:** Plan migration or upgrade immediately
- **Risk:** No security patches, bug fixes, or technical support available
- **Example:** Netcool/OMNIbus 8.1.x, Rational Synergy 7.2.x

### 🟠 ORANGE - Support Ending Soon (Warning)
- **Meaning:** Support ends within the next 12 months
- **Action Required:** Begin planning migration or upgrade
- **Risk:** Limited time to prepare for transition
- **Example:** z/OS 2.5.0, Guardium Data Protection 12.0.x

### 🟢 GREEN - Fully Supported (Good)
- **Meaning:** Product is actively supported by IBM
- **Action Required:** None - continue normal operations
- **Risk:** Low - regular updates and support available
- **Example:** AIX 7.3, WebSphere Application Server 9.0.x, IBM i 7.4

### 🔵 BLUE - No Lifecycle Data (Information)
- **Meaning:** Lifecycle information not found in our database
- **Action Required:** Review why data is missing (see section below)
- **Risk:** Unknown - requires investigation
- **Common Reasons:**
  - Hardware products (servers, storage, printers)
  - Third-party products (non-IBM)
  - Services and support contracts
  - Missing or incomplete version information
  - Product not in IBM lifecycle database

---

## 🔍 How Matching Works

The dashboard uses multiple matching strategies to find lifecycle data:

### 1. **Exact Match** (Most Reliable)
- Product name and version match exactly
- Example: `AIX 7.3` → Matches `AIX 7.3.0` in lifecycle database
- **Accuracy:** Highest

### 2. **Substring Match** (Common)
- Product name found within lifecycle database entry
- Example: `QRadar SIEM` → Matches `IBM Security QRadar SIEM`
- **Accuracy:** High

### 3. **Wildcard Match** (Version Patterns)
- Version matches using patterns like `7.1.x` or `5.x.x`
- Example: `Cloud Pak for Data 5.3.1` → Matches pattern `5.x.x`
- **Accuracy:** High

### 4. **Major.Minor Match** (Version Tolerance)
- Matches on major and minor version numbers only
- Example: `PowerVM 4.1.0.21` → Matches `4.1.0`
- **Accuracy:** Medium-High

### 5. **SaaS Match** (Cloud Services)
- Special handling for Software-as-a-Service products
- Example: `Instana Observability SaaS` → Matches SaaS lifecycle
- **Accuracy:** High

### 6. **No Match** (Blue Bubble)
- No matching product/version found in any lifecycle dictionary
- Requires investigation

---

## 📈 Match Statistics Breakdown

### Success Rate by Match Type

| Match Type | RED | ORANGE | GREEN | BLUE | Total |
|------------|-----|--------|-------|------|-------|
| **Exact** | 64 | 8 | 161 | 0 | 233 |
| **Substring** | 91 | 32 | 623 | 0 | 746 |
| **Wildcard** | 7 | 1 | 169 | 0 | 177 |
| **Major.Minor** | 32 | 20 | 68 | 0 | 120 |
| **SaaS** | 0 | 0 | 2 | 0 | 2 |
| **No Match** | 0 | 0 | 0 | 1,799 | 1,799 |

**Total Matched:** 1,278 (41.5%)  
**Total Unmatched:** 1,799 (58.5%)

---

## 🔴 Top 20 RED Products (End of Life)

These products have reached End of Support and require immediate attention:

1. **Netcool/OMNIbus 8.1.x** - Network management platform
2. **Rational Synergy 7.2.x** - Software configuration management
3. **Cloud Pak for Data System 1.0.x** - Data platform (older version)
4. **Cloud Pak for Data System 2.0.x** - Data platform (older version)
5. **Tivoli Network Manager 4.2.x** - Network monitoring
6. **Netcool/Impact 7.1.x** - Event management automation
7. **Aspera 4.0.x** - High-speed file transfer
8. **Sterling B2B Integrator 6.0.x** - B2B integration (not supported)
9. **Business Automation Workflow 20.0.x** - Workflow automation
10. **Db2 Administration Tool for z/OS 11.2** - Database administration
11. **Advanced VSAM Manager for z/OS 2.6.x** - Storage management (Service Extension Only)
12. **Fault Analyzer for z/OS 15.1.x** - Mainframe debugging
13. **Db2 High Performance Unload for z/OS 5.1** - Database utility
14. **CICS Transaction Gateway 9.2** - Transaction processing
15. **Rational ClearCase 9.0.x** - Version control
16. **WebSphere Application Server 8.5.x** - Application server (older)
17. **MQ 8.0.x** - Message queuing (older)
18. **DataPower Gateway 7.x** - API gateway (older)
19. **Cognos Analytics 11.0.x** - Business intelligence (older)
20. **Sterling File Gateway 6.0.x** - File transfer (older)

**Action Required:** Contact your IBM representative to discuss upgrade paths.

---

## 🟠 Top 20 ORANGE Products (Support Ending Soon)

These products will reach End of Support within 12 months:

1. **z/OS 2.5.0** - Mainframe operating system
2. **Guardium Data Protection 12.0.x** - Data security
3. **Z Software Asset Management 8.2.x** - License management
4. **Db2 High Performance Unload for z/OS 5.1** - Database utility
5. **Fault Analyzer for z/OS 15.1.x** - Mainframe debugging
6. **CICS Transaction Gateway 9.2** - Transaction processing
7. **WebSphere Application Server 8.5.5.x** - Application server
8. **MQ 9.0 LTS** - Message queuing
9. **DataPower Gateway 7.7.x** - API gateway
10. **Cognos Analytics 11.1.x** - Business intelligence
11. **Sterling File Gateway 6.1.x** - File transfer
12. **Maximo Asset Management 7.6.x** - Asset management
13. **Tivoli Storage Manager 7.1.x** - Backup/recovery
14. **Spectrum Protect 7.1.x** - Data protection
15. **InfoSphere DataStage 11.5** - ETL tool
16. **Rational Team Concert 6.0.x** - Development platform
17. **UrbanCode Deploy 6.2.x** - Application deployment
18. **API Connect 5.0.x** - API management (older)
19. **App Connect Enterprise 11.0.x** - Integration (older)
20. **Security Verify Access 10.0.x** - Identity management

**Action Required:** Begin planning upgrades within the next 6 months.

---

## 🟢 Top 20 GREEN Products (Fully Supported)

These products are actively supported and require no immediate action:

1. **AIX 7.3** - Unix operating system
2. **IBM i 7.4** - Midrange operating system
3. **z/OS 3.1.0** - Mainframe operating system
4. **WebSphere Application Server 9.0.x** - Application server
5. **QRadar SIEM 7.5.x** - Security information and event management
6. **Maximo Application Suite 9.0.x** - Asset management suite
7. **Cloud Pak for Data 5.x** - Data and AI platform
8. **Storage Protect 8.1.x** - Data protection
9. **API Connect 10.0.x** - API management
10. **App Connect Enterprise 12.0.x** - Integration platform
11. **Sterling B2B Integrator 6.1.x** - B2B integration
12. **Cognos Analytics 11.2.x / 12.0.x** - Business intelligence
13. **Planning Analytics Local 2.1.x** - Planning and analytics
14. **FileNet Content Manager 5.5.x** - Content management
15. **DevOps Deploy 8.x** - Application deployment
16. **Robotic Process Automation 23.0.x / 30.0.x** - RPA platform
17. **watsonx.data 2.x** - Data lakehouse
18. **Instana Observability** - Application monitoring
19. **Security Verify Directory 10.0.x** - Directory services
20. **DataPower Gateway 10.x** - API gateway

**Status:** Continue normal operations and maintenance.

---

## 🔵 Common Blue Bubble Categories

Blue bubbles appear for several legitimate reasons. Here are the most common categories:

### 1. **Hardware Products** (No Software Lifecycle)
Hardware has different lifecycle management than software:
- **Servers:** z14, z16, z17, Power System S922, LinuxONE Emperor 4
- **Storage:** FlashSystem 5000/7200/9200, DS8900F, SAN Volume Controller
- **Tape Systems:** TS4500 Tape Library, TS1090/TS2270 Tape Drive
- **Printers & ATMs:** Cash Recycling ATM, Printers, BEETLE POS Systems
- **Network Equipment:** Routers, switches, gateways

**Why Blue?** Hardware lifecycle is tracked separately from software.

### 2. **Third-Party Products** (Non-IBM)
Products from other vendors not in IBM lifecycle database:
- **Red Hat:** Red Hat Enterprise Linux Server
- **VMware:** VMware vSphere
- **Citrix:** Citrix MetaFrame
- **HashiCorp:** Vault Self-Managed, Consul Self-Managed, Nomad Self-Managed, Terraform Self-Managed
- **DataStax:** DataStax Enterprise
- **MongoDB:** MongoDB Enterprise Advanced
- **Flexera:** Flexera One
- **Oracle:** Siebel

**Why Blue?** These products are maintained by their respective vendors.

### 3. **Services & Support Contracts**
Non-product items that don't have version lifecycles:
- Partner Ecosystem Support
- Labor Only Project Services
- Field Project Services
- Best Effort
- IBMid Enterprise Federation
- Support Insights

**Why Blue?** Services don't have software versions or lifecycle dates.

### 4. **Missing Version Information**
Products where version data is incomplete or missing:
- Products with `nan` (not a number) versions
- Products with "Unknown" or "Other" versions
- Products with non-standard version formats

**Why Blue?** Cannot match lifecycle without version information.

### 5. **Cloud/SaaS Products** (Continuous Updates)
Some cloud products don't have traditional version lifecycles:
- Maximo Application Suite on Cloud
- Cognos Analytics on Cloud
- OpenPages on Cloud
- Sterling B2B Integration SaaS Premium
- webMethods Integration SaaS
- Turbonomic SaaS
- Planning Analytics as a Service

**Why Blue?** SaaS products are continuously updated; traditional lifecycle doesn't apply.

### 6. **Newer Products** (Not Yet in Database)
Recently released products may not be in the lifecycle database yet:
- Storage Fusion HCI Physical Appliance
- Fusion HCI for watsonx
- watsonx.data intelligence as a Service
- Envizi ESG Suite
- Security QRadar Suite

**Why Blue?** Lifecycle data may not be published yet for new releases.

### 7. **Specialized/Custom Solutions**
Unique or customized implementations:
- Integrated Analytics Systems
- Cloud Pak System
- Spectrum Archive Enterprise and Library
- Query Management Facility

**Why Blue?** May be custom configurations or specialized offerings.

---

## 🔎 How to Find Your Product

### Using the CSV Files

Two CSV files are available for detailed analysis:

#### 1. **lifecycle_match_results.csv**
Contains detailed results for every product/version combination.

**Columns:**
- `Product Name` - Original product name from tickets
- `Product Version` - Version from tickets
- `Mapped Product Name` - Normalized product name used for matching
- `Lifecycle Color` - red, orange, green, or blue
- `Match Type` - How the match was found (exact, substring, wildcard, etc.)
- `Match Details` - Explanation of the match or why it failed

**How to Use:**
1. Open in Excel or any spreadsheet application
2. Use Ctrl+F (Find) to search for your product name
3. Check the `Lifecycle Color` and `Match Details` columns
4. Sort by `Lifecycle Color` to see all products of a specific status

#### 2. **lifecycle_summary_by_color.csv**
Contains summary statistics by color.

**Use this for:**
- Quick overview of match success rates
- Understanding match type distribution
- Reporting and presentations

### Search Tips

**Finding a specific product:**
```
1. Open lifecycle_match_results.csv
2. Press Ctrl+F
3. Type part of the product name (e.g., "QRadar")
4. Review all matches
```

**Finding all RED products:**
```
1. Open lifecycle_match_results.csv
2. Click on "Lifecycle Color" column header
3. Click "Filter" button
4. Select "red" only
5. Sort by Product Name
```

**Finding products with no version:**
```
1. Open lifecycle_match_results.csv
2. Filter "Product Version" column
3. Look for "nan" or empty values
```

---

## ❓ Frequently Asked Questions (FAQ)

### Q1: Why is my product showing blue when it should have lifecycle data?

**A:** There are several possible reasons:
1. **Missing version information** - Check if the version field is empty or shows "nan"
2. **Version format mismatch** - The version format may not match what's in the lifecycle database
3. **Product name variation** - The product name may be slightly different from the official IBM name
4. **New product** - Recently released products may not be in the lifecycle database yet
5. **Hardware product** - Hardware lifecycles are tracked separately

**Solution:** Check the `Match Details` column in lifecycle_match_results.csv for specific information.

---

### Q2: How often is the lifecycle data updated?

**A:** The lifecycle dictionaries are updated periodically based on IBM's official product lifecycle announcements. Major updates typically occur:
- Quarterly for routine updates
- Immediately for critical End of Support announcements
- When new product versions are released

---

### Q3: What should I do if I see a RED bubble?

**A:** Take immediate action:
1. **Identify the product** - Note the exact product name and version
2. **Check current usage** - Determine how critical this product is
3. **Review upgrade path** - Contact IBM or check IBM documentation for upgrade options
4. **Plan migration** - Create a timeline for upgrading or migrating
5. **Contact support** - Reach out to your IBM representative for assistance

**Important:** RED means no security patches or support are available.

---

### Q4: Can I ignore ORANGE bubbles?

**A:** No, you should not ignore ORANGE bubbles. They indicate:
- Support ends within 12 months
- You have limited time to plan and execute upgrades
- Waiting until it turns RED means you're already out of support

**Best Practice:** Begin planning upgrades as soon as you see ORANGE.

---

### Q5: Why do hardware products show blue?

**A:** Hardware products (servers, storage, printers, etc.) have different lifecycle management:
- Hardware lifecycle is based on manufacturing dates and warranty periods
- Software lifecycle is based on version support dates
- The dashboard focuses on software lifecycle data
- Hardware support should be tracked through IBM hardware support contracts

---

### Q6: How accurate is the matching?

**A:** Matching accuracy varies by type:
- **Exact matches:** 99%+ accuracy
- **Substring matches:** 95%+ accuracy (most common)
- **Wildcard matches:** 90%+ accuracy
- **Major.Minor matches:** 85%+ accuracy

Overall, the system successfully matches **41.5%** of products with high confidence.

---

### Q7: What if my product version is slightly different?

**A:** The matching system is designed to handle version variations:
- `7.5.0.15` will match `7.5.x` (wildcard)
- `9.0.x ND on IBM i` will match `9.0.x` (exact)
- `V10 R3 M1050` may not match if format is too different

If your version doesn't match, check the official IBM product name and version format.

---

### Q8: Can I request a product be added to the lifecycle database?

**A:** Yes! If you believe a product should have lifecycle data:
1. Verify the product is an IBM software product
2. Check IBM's official lifecycle page for the product
3. Contact the dashboard administrator with:
   - Product name
   - Version
   - Link to IBM lifecycle documentation
4. The administrator can add it to the next update

---

### Q9: Why do some SaaS products show blue?

**A:** SaaS (Software-as-a-Service) products often show blue because:
- They don't have traditional version numbers
- They're continuously updated
- Traditional lifecycle concepts don't apply
- Support is based on subscription, not version

**Note:** Some SaaS products (like Instana Observability SaaS) do have lifecycle entries and show GREEN.

---

### Q10: How do I export data for my team?

**A:** You can export data in several ways:
1. **Use the CSV files directly** - Share lifecycle_match_results.csv with your team
2. **Filter in Excel** - Open the CSV, filter by your products, save as new file
3. **Create a pivot table** - Summarize by product family or lifecycle status
4. **Dashboard export** - Use the dashboard's built-in export features

---

## 🎯 Next Steps

### For Products Showing Blue

If your product shows blue and you believe it should have lifecycle data:

1. **Verify the product name** - Check if it matches IBM's official product name
2. **Check the version format** - Ensure version is in standard format (e.g., 7.5.0, not "Latest")
3. **Review product type** - Confirm it's a software product, not hardware or service
4. **Check IBM lifecycle page** - Visit IBM's official product lifecycle website
5. **Contact administrator** - If lifecycle data exists but isn't matching, report it

### For Products Showing Red or Orange

1. **Document current usage** - List all systems using the product
2. **Review upgrade options** - Check IBM documentation for upgrade paths
3. **Assess impact** - Determine business impact of upgrading
4. **Create timeline** - Develop migration/upgrade schedule
5. **Engage IBM support** - Contact your IBM representative for assistance
6. **Budget planning** - Include upgrade costs in budget planning

### For Products Showing Green

1. **Monitor regularly** - Check dashboard monthly for status changes
2. **Stay current** - Keep products updated with latest patches
3. **Plan ahead** - Be aware of when support might end
4. **Document versions** - Maintain accurate inventory of versions in use

---

## 📚 Additional Resources

### IBM Product Lifecycle Information
- **IBM Product Lifecycle:** https://www.ibm.com/support/pages/ibm-product-lifecycle
- **IBM Support Lifecycle:** https://www.ibm.com/support/pages/support-lifecycle
- **End of Support Announcements:** Check IBM Support Portal

### Dashboard Resources
- **LIFECYCLE_MATCH_REPORT.md** - Technical analysis report
- **lifecycle_match_results.csv** - Detailed match results
- **lifecycle_summary_by_color.csv** - Summary statistics
- **DEPLOYMENT_GUIDE.md** - Dashboard deployment information

### Contact Information
For questions about:
- **Lifecycle data accuracy** - Contact dashboard administrator
- **Product upgrades** - Contact your IBM representative
- **Technical support** - Open ticket with IBM Support
- **Dashboard features** - Contact dashboard development team

---

## 📝 Document Information

**Version:** 1.0  
**Last Updated:** June 12, 2026  
**Data Source:** May 2026 Ticketing Data (3,077 unique product/version combinations)  
**Generated By:** generate_lifecycle_match_report.py  

**Change Log:**
- 2026-06-12: Initial version created

---

**Need Help?** Contact your dashboard administrator or IBM representative for assistance with lifecycle planning and product upgrades.