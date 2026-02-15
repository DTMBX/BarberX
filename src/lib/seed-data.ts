import { Jurisdiction, Document, Section, LearningModule } from './types'
import { usConstitutionSections } from './us-constitution-full'

export const jurisdictions: Jurisdiction[] = [
  {
    id: 'us-federal',
    name: 'United States (Federal)',
    type: 'federal',
    abbreviation: 'U.S.'
  },
  {
    id: 'us-al',
    name: 'Alabama',
    type: 'state',
    abbreviation: 'AL',
    parentId: 'us-federal'
  },
  {
    id: 'us-ak',
    name: 'Alaska',
    type: 'state',
    abbreviation: 'AK',
    parentId: 'us-federal'
  },
  {
    id: 'us-az',
    name: 'Arizona',
    type: 'state',
    abbreviation: 'AZ',
    parentId: 'us-federal'
  },
  {
    id: 'us-ar',
    name: 'Arkansas',
    type: 'state',
    abbreviation: 'AR',
    parentId: 'us-federal'
  },
  {
    id: 'us-ca',
    name: 'California',
    type: 'state',
    abbreviation: 'CA',
    parentId: 'us-federal'
  },
  {
    id: 'us-co',
    name: 'Colorado',
    type: 'state',
    abbreviation: 'CO',
    parentId: 'us-federal'
  },
  {
    id: 'us-ct',
    name: 'Connecticut',
    type: 'state',
    abbreviation: 'CT',
    parentId: 'us-federal'
  },
  {
    id: 'us-de',
    name: 'Delaware',
    type: 'state',
    abbreviation: 'DE',
    parentId: 'us-federal'
  },
  {
    id: 'us-fl',
    name: 'Florida',
    type: 'state',
    abbreviation: 'FL',
    parentId: 'us-federal'
  },
  {
    id: 'us-ga',
    name: 'Georgia',
    type: 'state',
    abbreviation: 'GA',
    parentId: 'us-federal'
  },
  {
    id: 'us-hi',
    name: 'Hawaii',
    type: 'state',
    abbreviation: 'HI',
    parentId: 'us-federal'
  },
  {
    id: 'us-id',
    name: 'Idaho',
    type: 'state',
    abbreviation: 'ID',
    parentId: 'us-federal'
  },
  {
    id: 'us-il',
    name: 'Illinois',
    type: 'state',
    abbreviation: 'IL',
    parentId: 'us-federal'
  },
  {
    id: 'us-in',
    name: 'Indiana',
    type: 'state',
    abbreviation: 'IN',
    parentId: 'us-federal'
  },
  {
    id: 'us-ia',
    name: 'Iowa',
    type: 'state',
    abbreviation: 'IA',
    parentId: 'us-federal'
  },
  {
    id: 'us-ks',
    name: 'Kansas',
    type: 'state',
    abbreviation: 'KS',
    parentId: 'us-federal'
  },
  {
    id: 'us-ky',
    name: 'Kentucky',
    type: 'state',
    abbreviation: 'KY',
    parentId: 'us-federal'
  },
  {
    id: 'us-la',
    name: 'Louisiana',
    type: 'state',
    abbreviation: 'LA',
    parentId: 'us-federal'
  },
  {
    id: 'us-me',
    name: 'Maine',
    type: 'state',
    abbreviation: 'ME',
    parentId: 'us-federal'
  },
  {
    id: 'us-md',
    name: 'Maryland',
    type: 'state',
    abbreviation: 'MD',
    parentId: 'us-federal'
  },
  {
    id: 'us-ma',
    name: 'Massachusetts',
    type: 'state',
    abbreviation: 'MA',
    parentId: 'us-federal'
  },
  {
    id: 'us-mi',
    name: 'Michigan',
    type: 'state',
    abbreviation: 'MI',
    parentId: 'us-federal'
  },
  {
    id: 'us-mn',
    name: 'Minnesota',
    type: 'state',
    abbreviation: 'MN',
    parentId: 'us-federal'
  },
  {
    id: 'us-ms',
    name: 'Mississippi',
    type: 'state',
    abbreviation: 'MS',
    parentId: 'us-federal'
  },
  {
    id: 'us-mo',
    name: 'Missouri',
    type: 'state',
    abbreviation: 'MO',
    parentId: 'us-federal'
  },
  {
    id: 'us-mt',
    name: 'Montana',
    type: 'state',
    abbreviation: 'MT',
    parentId: 'us-federal'
  },
  {
    id: 'us-ne',
    name: 'Nebraska',
    type: 'state',
    abbreviation: 'NE',
    parentId: 'us-federal'
  },
  {
    id: 'us-nv',
    name: 'Nevada',
    type: 'state',
    abbreviation: 'NV',
    parentId: 'us-federal'
  },
  {
    id: 'us-nh',
    name: 'New Hampshire',
    type: 'state',
    abbreviation: 'NH',
    parentId: 'us-federal'
  },
  {
    id: 'us-nj',
    name: 'New Jersey',
    type: 'state',
    abbreviation: 'NJ',
    parentId: 'us-federal'
  },
  {
    id: 'us-nm',
    name: 'New Mexico',
    type: 'state',
    abbreviation: 'NM',
    parentId: 'us-federal'
  },
  {
    id: 'us-ny',
    name: 'New York',
    type: 'state',
    abbreviation: 'NY',
    parentId: 'us-federal'
  },
  {
    id: 'us-nc',
    name: 'North Carolina',
    type: 'state',
    abbreviation: 'NC',
    parentId: 'us-federal'
  },
  {
    id: 'us-nd',
    name: 'North Dakota',
    type: 'state',
    abbreviation: 'ND',
    parentId: 'us-federal'
  },
  {
    id: 'us-oh',
    name: 'Ohio',
    type: 'state',
    abbreviation: 'OH',
    parentId: 'us-federal'
  },
  {
    id: 'us-ok',
    name: 'Oklahoma',
    type: 'state',
    abbreviation: 'OK',
    parentId: 'us-federal'
  },
  {
    id: 'us-or',
    name: 'Oregon',
    type: 'state',
    abbreviation: 'OR',
    parentId: 'us-federal'
  },
  {
    id: 'us-pa',
    name: 'Pennsylvania',
    type: 'state',
    abbreviation: 'PA',
    parentId: 'us-federal'
  },
  {
    id: 'us-ri',
    name: 'Rhode Island',
    type: 'state',
    abbreviation: 'RI',
    parentId: 'us-federal'
  },
  {
    id: 'us-sc',
    name: 'South Carolina',
    type: 'state',
    abbreviation: 'SC',
    parentId: 'us-federal'
  },
  {
    id: 'us-sd',
    name: 'South Dakota',
    type: 'state',
    abbreviation: 'SD',
    parentId: 'us-federal'
  },
  {
    id: 'us-tn',
    name: 'Tennessee',
    type: 'state',
    abbreviation: 'TN',
    parentId: 'us-federal'
  },
  {
    id: 'us-tx',
    name: 'Texas',
    type: 'state',
    abbreviation: 'TX',
    parentId: 'us-federal'
  },
  {
    id: 'us-ut',
    name: 'Utah',
    type: 'state',
    abbreviation: 'UT',
    parentId: 'us-federal'
  },
  {
    id: 'us-vt',
    name: 'Vermont',
    type: 'state',
    abbreviation: 'VT',
    parentId: 'us-federal'
  },
  {
    id: 'us-va',
    name: 'Virginia',
    type: 'state',
    abbreviation: 'VA',
    parentId: 'us-federal'
  },
  {
    id: 'us-wa',
    name: 'Washington',
    type: 'state',
    abbreviation: 'WA',
    parentId: 'us-federal'
  },
  {
    id: 'us-wv',
    name: 'West Virginia',
    type: 'state',
    abbreviation: 'WV',
    parentId: 'us-federal'
  },
  {
    id: 'us-wi',
    name: 'Wisconsin',
    type: 'state',
    abbreviation: 'WI',
    parentId: 'us-federal'
  },
  {
    id: 'us-wy',
    name: 'Wyoming',
    type: 'state',
    abbreviation: 'WY',
    parentId: 'us-federal'
  },
  {
    id: 'us-dc',
    name: 'District of Columbia',
    type: 'territory',
    abbreviation: 'DC',
    parentId: 'us-federal'
  },
  {
    id: 'us-pr',
    name: 'Puerto Rico',
    type: 'territory',
    abbreviation: 'PR',
    parentId: 'us-federal'
  },
  {
    id: 'us-vi',
    name: 'U.S. Virgin Islands',
    type: 'territory',
    abbreviation: 'VI',
    parentId: 'us-federal'
  },
  {
    id: 'us-gu',
    name: 'Guam',
    type: 'territory',
    abbreviation: 'GU',
    parentId: 'us-federal'
  },
  {
    id: 'us-as',
    name: 'American Samoa',
    type: 'territory',
    abbreviation: 'AS',
    parentId: 'us-federal'
  },
  {
    id: 'us-mp',
    name: 'Northern Mariana Islands',
    type: 'territory',
    abbreviation: 'MP',
    parentId: 'us-federal'
  }
]

const stateConstitutions: Document[] = [
  { id: 'al-constitution', title: 'Alabama Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-al', effectiveDate: '1901-11-28', verificationStatus: 'official', sourceUrl: 'https://www.legislature.state.al.us/aliswww/constitution/constitution.html', description: 'The governing document of the State of Alabama' },
  { id: 'ak-constitution', title: 'Alaska Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ak', effectiveDate: '1959-01-03', verificationStatus: 'official', sourceUrl: 'http://www.legis.state.ak.us/basis/folioproxy.asp?url=http://wwwjnu01.legis.state.ak.us/cgi-bin/folioisa.dll/acontxt.nfo', description: 'The governing document of the State of Alaska' },
  { id: 'az-constitution', title: 'Arizona Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-az', effectiveDate: '1912-02-14', verificationStatus: 'official', sourceUrl: 'https://www.azleg.gov/constitution/', description: 'The governing document of the State of Arizona' },
  { id: 'ar-constitution', title: 'Arkansas Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ar', effectiveDate: '1874-10-13', verificationStatus: 'official', sourceUrl: 'https://www.arkleg.state.ar.us/Bills/FTPDocument?path=%2FConstitution%2F', description: 'The governing document of the State of Arkansas' },
  { id: 'ca-constitution', title: 'California Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ca', effectiveDate: '1879-07-04', verificationStatus: 'official', sourceUrl: 'https://leginfo.legislature.ca.gov/faces/codes.xhtml', description: 'The governing document of the State of California' },
  { id: 'co-constitution', title: 'Colorado Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-co', effectiveDate: '1876-08-01', verificationStatus: 'official', sourceUrl: 'https://leg.colorado.gov/colorado-constitution', description: 'The governing document of the State of Colorado' },
  { id: 'ct-constitution', title: 'Connecticut Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ct', effectiveDate: '1965-12-30', verificationStatus: 'official', sourceUrl: 'https://cga.ct.gov/current/pub/chap_001.htm', description: 'The governing document of the State of Connecticut' },
  { id: 'de-constitution', title: 'Delaware Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-de', effectiveDate: '1897-06-10', verificationStatus: 'official', sourceUrl: 'https://delcode.delaware.gov/constitution/', description: 'The governing document of the State of Delaware' },
  { id: 'fl-constitution', title: 'Florida Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-fl', effectiveDate: '1968-01-07', verificationStatus: 'official', sourceUrl: 'http://www.leg.state.fl.us/Statutes/index.cfm?Mode=Constitution', description: 'The governing document of the State of Florida' },
  { id: 'ga-constitution', title: 'Georgia Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ga', effectiveDate: '1983-07-01', verificationStatus: 'official', sourceUrl: 'https://www.legis.ga.gov/api/legislation/document/20212022/201498', description: 'The governing document of the State of Georgia' },
  { id: 'hi-constitution', title: 'Hawaii Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-hi', effectiveDate: '1959-08-21', verificationStatus: 'official', sourceUrl: 'https://lrb.hawaii.gov/constitution', description: 'The governing document of the State of Hawaii' },
  { id: 'id-constitution', title: 'Idaho Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-id', effectiveDate: '1890-07-03', verificationStatus: 'official', sourceUrl: 'https://legislature.idaho.gov/statutesrules/idconst/', description: 'The governing document of the State of Idaho' },
  { id: 'il-constitution', title: 'Illinois Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-il', effectiveDate: '1971-07-01', verificationStatus: 'official', sourceUrl: 'https://www.ilga.gov/commission/lrb/conmain.htm', description: 'The governing document of the State of Illinois' },
  { id: 'in-constitution', title: 'Indiana Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-in', effectiveDate: '1851-11-01', verificationStatus: 'official', sourceUrl: 'http://iga.in.gov/legislative/laws/const/', description: 'The governing document of the State of Indiana' },
  { id: 'ia-constitution', title: 'Iowa Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ia', effectiveDate: '1857-09-03', verificationStatus: 'official', sourceUrl: 'https://www.legis.iowa.gov/law/iowaConstitution', description: 'The governing document of the State of Iowa' },
  { id: 'ks-constitution', title: 'Kansas Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ks', effectiveDate: '1861-01-29', verificationStatus: 'official', sourceUrl: 'http://www.kslegislature.org/li/b2021_22/statute/constitution/', description: 'The governing document of the State of Kansas' },
  { id: 'ky-constitution', title: 'Kentucky Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ky', effectiveDate: '1891-09-28', verificationStatus: 'official', sourceUrl: 'https://legislature.ky.gov/Law/Constitution/Pages/default.aspx', description: 'The governing document of the Commonwealth of Kentucky' },
  { id: 'la-constitution', title: 'Louisiana Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-la', effectiveDate: '1975-01-01', verificationStatus: 'official', sourceUrl: 'https://www.legis.la.gov/legis/Laws_Toc.aspx?folder=Constitution&level=Parent', description: 'The governing document of the State of Louisiana' },
  { id: 'me-constitution', title: 'Maine Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-me', effectiveDate: '1820-03-15', verificationStatus: 'official', sourceUrl: 'https://legislature.maine.gov/lawlibrary/constitution-of-maine/9623', description: 'The governing document of the State of Maine' },
  { id: 'md-constitution', title: 'Maryland Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-md', effectiveDate: '1867-10-05', verificationStatus: 'official', sourceUrl: 'https://msa.maryland.gov/msa/mdmanual/43const/html/const.html', description: 'The governing document of the State of Maryland' },
  { id: 'ma-constitution', title: 'Massachusetts Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ma', effectiveDate: '1780-10-25', verificationStatus: 'official', sourceUrl: 'https://malegislature.gov/Laws/Constitution', description: 'The governing document of the Commonwealth of Massachusetts' },
  { id: 'mi-constitution', title: 'Michigan Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-mi', effectiveDate: '1964-01-01', verificationStatus: 'official', sourceUrl: 'https://www.legislature.mi.gov/documents/Publications/Constitution.pdf', description: 'The governing document of the State of Michigan' },
  { id: 'mn-constitution', title: 'Minnesota Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-mn', effectiveDate: '1858-05-11', verificationStatus: 'official', sourceUrl: 'https://www.revisor.mn.gov/constitution/', description: 'The governing document of the State of Minnesota' },
  { id: 'ms-constitution', title: 'Mississippi Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ms', effectiveDate: '1890-11-01', verificationStatus: 'official', sourceUrl: 'https://www.sos.ms.gov/education-publications/Pages/Constitution.aspx', description: 'The governing document of the State of Mississippi' },
  { id: 'mo-constitution', title: 'Missouri Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-mo', effectiveDate: '1945-03-30', verificationStatus: 'official', sourceUrl: 'https://www.sos.mo.gov/cmsimages/archives/resources/findingaids/miscellaneous/mo_const.pdf', description: 'The governing document of the State of Missouri' },
  { id: 'mt-constitution', title: 'Montana Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-mt', effectiveDate: '1972-07-01', verificationStatus: 'official', sourceUrl: 'https://leg.mt.gov/bills/mca/Constitution/Index.html', description: 'The governing document of the State of Montana' },
  { id: 'ne-constitution', title: 'Nebraska Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ne', effectiveDate: '1875-10-12', verificationStatus: 'official', sourceUrl: 'https://nebraskalegislature.gov/laws/browse-constitution.php', description: 'The governing document of the State of Nebraska' },
  { id: 'nv-constitution', title: 'Nevada Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nv', effectiveDate: '1864-10-31', verificationStatus: 'official', sourceUrl: 'https://www.leg.state.nv.us/const/nvconst.html', description: 'The governing document of the State of Nevada' },
  { id: 'nh-constitution', title: 'New Hampshire Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nh', effectiveDate: '1784-06-02', verificationStatus: 'official', sourceUrl: 'https://www.nh.gov/constitution/', description: 'The governing document of the State of New Hampshire' },
  { id: 'nj-constitution', title: 'New Jersey Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nj', effectiveDate: '1948-01-01', verificationStatus: 'official', sourceUrl: 'https://www.njleg.state.nj.us/lawsconstitution/constitution.asp', description: 'The governing document of the State of New Jersey' },
  { id: 'nm-constitution', title: 'New Mexico Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nm', effectiveDate: '1912-01-06', verificationStatus: 'official', sourceUrl: 'https://www.nmlegis.gov/law/nm_constitution', description: 'The governing document of the State of New Mexico' },
  { id: 'ny-constitution', title: 'New York State Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ny', effectiveDate: '1895-01-01', verificationStatus: 'official', sourceUrl: 'https://www.nysenate.gov/legislation/constitution', description: 'The governing document of the State of New York' },
  { id: 'nc-constitution', title: 'North Carolina Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nc', effectiveDate: '1971-07-01', verificationStatus: 'official', sourceUrl: 'https://www.ncleg.gov/Laws/Constitution', description: 'The governing document of the State of North Carolina' },
  { id: 'nd-constitution', title: 'North Dakota Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-nd', effectiveDate: '1889-11-02', verificationStatus: 'official', sourceUrl: 'https://www.legis.nd.gov/constitution', description: 'The governing document of the State of North Dakota' },
  { id: 'oh-constitution', title: 'Ohio Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-oh', effectiveDate: '1851-09-01', verificationStatus: 'official', sourceUrl: 'https://codes.ohio.gov/ohio-constitution', description: 'The governing document of the State of Ohio' },
  { id: 'ok-constitution', title: 'Oklahoma Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ok', effectiveDate: '1907-11-16', verificationStatus: 'official', sourceUrl: 'http://www.oklegislature.gov/constitution.html', description: 'The governing document of the State of Oklahoma' },
  { id: 'or-constitution', title: 'Oregon Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-or', effectiveDate: '1859-02-14', verificationStatus: 'official', sourceUrl: 'https://www.oregonlegislature.gov/bills_laws/Pages/OrConst.aspx', description: 'The governing document of the State of Oregon' },
  { id: 'pa-constitution', title: 'Pennsylvania Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-pa', effectiveDate: '1968-04-23', verificationStatus: 'official', sourceUrl: 'https://www.legis.state.pa.us/cfdocs/legis/LI/consCheck.cfm', description: 'The governing document of the Commonwealth of Pennsylvania' },
  { id: 'ri-constitution', title: 'Rhode Island Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ri', effectiveDate: '1843-05-02', verificationStatus: 'official', sourceUrl: 'http://webserver.rilin.state.ri.us/RiConstitution/', description: 'The governing document of the State of Rhode Island' },
  { id: 'sc-constitution', title: 'South Carolina Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-sc', effectiveDate: '1895-12-31', verificationStatus: 'official', sourceUrl: 'https://www.scstatehouse.gov/scconstitution/scconst.php', description: 'The governing document of the State of South Carolina' },
  { id: 'sd-constitution', title: 'South Dakota Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-sd', effectiveDate: '1889-11-02', verificationStatus: 'official', sourceUrl: 'https://sdlegislature.gov/Statutes/Constitution', description: 'The governing document of the State of South Dakota' },
  { id: 'tn-constitution', title: 'Tennessee Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-tn', effectiveDate: '1870-05-05', verificationStatus: 'official', sourceUrl: 'https://www.tn.gov/sos/rules/tennessee-constitution.html', description: 'The governing document of the State of Tennessee' },
  { id: 'tx-constitution', title: 'Texas Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-tx', effectiveDate: '1876-02-15', verificationStatus: 'official', sourceUrl: 'https://statutes.capitol.texas.gov/', description: 'The governing document of the State of Texas' },
  { id: 'ut-constitution', title: 'Utah Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-ut', effectiveDate: '1896-01-04', verificationStatus: 'official', sourceUrl: 'https://le.utah.gov/xcode/const.html', description: 'The governing document of the State of Utah' },
  { id: 'vt-constitution', title: 'Vermont Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-vt', effectiveDate: '1793-07-09', verificationStatus: 'official', sourceUrl: 'https://legislature.vermont.gov/statutes/constitution', description: 'The governing document of the State of Vermont' },
  { id: 'va-constitution', title: 'Virginia Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-va', effectiveDate: '1971-07-01', verificationStatus: 'official', sourceUrl: 'https://law.lis.virginia.gov/constitution', description: 'The governing document of the Commonwealth of Virginia' },
  { id: 'wa-constitution', title: 'Washington State Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-wa', effectiveDate: '1889-11-11', verificationStatus: 'official', sourceUrl: 'https://leg.wa.gov/CodeReviser/Pages/WAConstitution.aspx', description: 'The governing document of the State of Washington' },
  { id: 'wv-constitution', title: 'West Virginia Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-wv', effectiveDate: '1863-06-20', verificationStatus: 'official', sourceUrl: 'http://www.wvlegislature.gov/wvcode/WV_CON.cfm', description: 'The governing document of the State of West Virginia' },
  { id: 'wi-constitution', title: 'Wisconsin Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-wi', effectiveDate: '1848-05-29', verificationStatus: 'official', sourceUrl: 'https://docs.legis.wisconsin.gov/constitution', description: 'The governing document of the State of Wisconsin' },
  { id: 'wy-constitution', title: 'Wyoming Constitution', type: 'constitution', authorityLevel: 'state', jurisdictionId: 'us-wy', effectiveDate: '1890-07-10', verificationStatus: 'official', sourceUrl: 'https://law.justia.com/constitution/wyoming/', description: 'The governing document of the State of Wyoming' }
]

const territoryDocuments: Document[] = [
  { id: 'dc-home-rule-act', title: 'District of Columbia Home Rule Act', type: 'organic-act', authorityLevel: 'territory', jurisdictionId: 'us-dc', effectiveDate: '1973-12-24', verificationStatus: 'official', sourceUrl: 'https://code.dccouncil.gov/us/dc/council/code/titles/1/chapters/2/', description: 'Organic act establishing self-government for the District of Columbia' },
  { id: 'pr-constitution', title: 'Constitution of Puerto Rico', type: 'constitution', authorityLevel: 'territory', jurisdictionId: 'us-pr', effectiveDate: '1952-07-25', verificationStatus: 'official', sourceUrl: 'https://www.lexjuris.com/lexprcont.htm', description: 'The governing document of the Commonwealth of Puerto Rico' },
  { id: 'vi-organic-act', title: 'Virgin Islands Revised Organic Act', type: 'organic-act', authorityLevel: 'territory', jurisdictionId: 'us-vi', effectiveDate: '1954-07-22', verificationStatus: 'official', sourceUrl: 'https://www.law.cornell.edu/uscode/text/48/chapter-12/subchapter-III', description: 'Organic act establishing the government of the U.S. Virgin Islands' },
  { id: 'gu-organic-act', title: 'Guam Organic Act', type: 'organic-act', authorityLevel: 'territory', jurisdictionId: 'us-gu', effectiveDate: '1950-08-01', verificationStatus: 'official', sourceUrl: 'https://www.law.cornell.edu/uscode/text/48/chapter-8A', description: 'Organic act establishing civilian government for Guam' },
  { id: 'as-constitution', title: 'American Samoa Constitution', type: 'constitution', authorityLevel: 'territory', jurisdictionId: 'us-as', effectiveDate: '1967-07-01', verificationStatus: 'official', sourceUrl: 'https://new.asbar.org/american-samoa-code/', description: 'The governing document of American Samoa' },
  { id: 'mp-constitution', title: 'Commonwealth of the Northern Mariana Islands Constitution', type: 'constitution', authorityLevel: 'territory', jurisdictionId: 'us-mp', effectiveDate: '1978-01-09', verificationStatus: 'official', sourceUrl: 'https://www.cnmilaw.org/constitution.htm', description: 'The governing document of the Northern Mariana Islands' }
]

const federalStatutes: Document[] = [
  { id: 'usc-title-18', title: 'United States Code Title 18 - Crimes and Criminal Procedure', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', verificationStatus: 'official', sourceUrl: 'https://uscode.house.gov/view.xhtml?path=/prelim@title18&edition=prelim', description: 'Federal criminal law' },
  { id: 'usc-title-42', title: 'United States Code Title 42 - The Public Health and Welfare', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', verificationStatus: 'official', sourceUrl: 'https://uscode.house.gov/view.xhtml?path=/prelim@title42&edition=prelim', description: 'Federal public health, social security, and civil rights law' },
  { id: 'civil-rights-act-1964', title: 'Civil Rights Act of 1964', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1964-07-02', verificationStatus: 'official', sourceUrl: 'https://www.archives.gov/milestone-documents/civil-rights-act', description: 'Landmark civil rights and labor law prohibiting discrimination' },
  { id: 'voting-rights-act-1965', title: 'Voting Rights Act of 1965', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1965-08-06', verificationStatus: 'official', sourceUrl: 'https://www.archives.gov/milestone-documents/voting-rights-act', description: 'Prohibits racial discrimination in voting' },
  { id: 'ada-1990', title: 'Americans with Disabilities Act of 1990', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1990-07-26', verificationStatus: 'official', sourceUrl: 'https://www.ada.gov/law-and-regs/ada/', description: 'Civil rights law prohibiting discrimination based on disability' },
  { id: 'foia', title: 'Freedom of Information Act', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1967-07-04', verificationStatus: 'official', sourceUrl: 'https://www.foia.gov/', description: 'Provides public access to federal government information' },
  { id: 'privacy-act-1974', title: 'Privacy Act of 1974', type: 'statute', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1975-09-27', verificationStatus: 'official', sourceUrl: 'https://www.justice.gov/opcl/privacy-act-1974', description: 'Governs collection, maintenance, use, and dissemination of personal information by federal agencies' }
]

const treaties: Document[] = [
  { id: 'treaty-un-charter', title: 'Charter of the United Nations', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1945-10-24', verificationStatus: 'official', sourceUrl: 'https://www.un.org/en/about-us/un-charter', description: 'Foundational treaty of the United Nations' },
  { id: 'treaty-geneva-conventions', title: 'Geneva Conventions', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1949-08-12', verificationStatus: 'official', sourceUrl: 'https://www.icrc.org/en/war-and-law/treaties-customary-law/geneva-conventions', description: 'International humanitarian law treaties' },
  { id: 'treaty-nato', title: 'North Atlantic Treaty (NATO)', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1949-04-04', verificationStatus: 'official', sourceUrl: 'https://www.nato.int/cps/en/natolive/official_texts_17120.htm', description: 'Collective defense treaty' },
  { id: 'treaty-udhr', title: 'Universal Declaration of Human Rights', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1948-12-10', verificationStatus: 'official', sourceUrl: 'https://www.un.org/en/about-us/universal-declaration-of-human-rights', description: 'International declaration of human rights standards' },
  { id: 'treaty-iccpr', title: 'International Covenant on Civil and Political Rights', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1976-03-23', verificationStatus: 'official', sourceUrl: 'https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights', description: 'UN treaty on civil and political rights' },
  { id: 'treaty-cerd', title: 'International Convention on the Elimination of All Forms of Racial Discrimination', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1969-01-04', verificationStatus: 'official', sourceUrl: 'https://www.ohchr.org/en/instruments-mechanisms/instruments/international-convention-elimination-all-forms-racial', description: 'UN treaty against racial discrimination' },
  { id: 'treaty-cat', title: 'Convention Against Torture', type: 'treaty', authorityLevel: 'federal', jurisdictionId: 'us-federal', effectiveDate: '1987-06-26', verificationStatus: 'official', sourceUrl: 'https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-against-torture-and-other-cruel-inhuman-or-degrading', description: 'UN treaty prohibiting torture' }
]

export const documents: Document[] = [
  {
    id: 'us-constitution',
    title: 'Constitution of the United States',
    type: 'constitution',
    authorityLevel: 'federal',
    jurisdictionId: 'us-federal',
    effectiveDate: '1789-03-04',
    verificationStatus: 'official',
    sourceUrl: 'https://www.archives.gov/founding-docs/constitution',
    description: 'The supreme law of the United States of America'
  },
  ...stateConstitutions,
  ...territoryDocuments,
  ...federalStatutes,
  ...treaties
]

const stateConstitutionSections = (): Section[] => {
  const stateData = [
    { id: 'al', abbr: 'Ala.', preamble: 'We, the people of the State of Alabama, invoking the favor and guidance of Almighty God, do ordain and establish the following Constitution and form of government for the State of Alabama.', billOfRights: 'That all men are equally free and independent; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty and the pursuit of happiness.' },
    { id: 'ak', abbr: 'Alaska', preamble: 'We the people of Alaska, grateful to God and to those who founded our nation and pioneered this great land, do ordain and establish this constitution for the State of Alaska.', billOfRights: 'This constitution is dedicated to the principles that all persons have a natural right to life, liberty, the pursuit of happiness, and the enjoyment of the rewards of their own industry.' },
    { id: 'az', abbr: 'Ariz.', preamble: 'We, the people of the State of Arizona, grateful to Almighty God for our liberties, do ordain this Constitution.', billOfRights: 'A frequent recurrence to fundamental principles is essential to the security of individual rights and the perpetuity of free government.' },
    { id: 'ar', abbr: 'Ark.', preamble: 'We, the People of the State of Arkansas, grateful to Almighty God for the privilege of choosing our own form of government, do ordain and establish this Constitution.', billOfRights: 'All men are created equally free and independent, and have certain inherent and inalienable rights, amongst which are those of enjoying and defending life and liberty.' },
    { id: 'ca', abbr: 'Cal.', preamble: 'We, the People of the State of California, grateful to Almighty God for our freedom, do establish this Constitution.', billOfRights: 'All people are by nature free and independent and have inalienable rights. Among these are enjoying and defending life and liberty, acquiring, possessing, and protecting property, and pursuing and obtaining safety, happiness, and privacy.' },
    { id: 'co', abbr: 'Colo.', preamble: 'We, the people of Colorado, with profound reverence for the Supreme Ruler of the Universe, do ordain and establish this constitution for the State of Colorado.', billOfRights: 'All persons have certain natural, essential and inalienable rights, among which may be reckoned the right of enjoying and defending their lives and liberties.' },
    { id: 'ct', abbr: 'Conn.', preamble: 'The People of Connecticut acknowledging with gratitude, the good providence of God, do ordain and establish this Constitution.', billOfRights: 'All men when they form a social compact, are equal in rights; and no man or set of men are entitled to exclusive public emoluments or privileges from the community.' },
    { id: 'de', abbr: 'Del.', preamble: 'Through Divine goodness, all people have by nature the rights of worshiping and serving their Creator according to the dictates of their consciences.', billOfRights: 'All government of right originates from the people, is founded in compact only, and instituted solely for the good of the whole.' },
    { id: 'fl', abbr: 'Fla.', preamble: 'We, the people of the State of Florida, being grateful to Almighty God for our constitutional liberty, do ordain and establish this constitution.', billOfRights: 'All natural persons, female and male alike, are equal before the law and have inalienable rights, among which are the right to enjoy and defend life and liberty, to pursue happiness, to be rewarded for industry, and to acquire, possess and protect property.' },
    { id: 'ga', abbr: 'Ga.', preamble: 'To perpetuate the principles of free government, insure justice to all, preserve peace, promote the interest and happiness of the citizen, we the people of Georgia, do ordain and establish this Constitution.', billOfRights: 'No person shall be deprived of life, liberty, or property except by due process of law. All persons are equal before the law.' },
    { id: 'hi', abbr: 'Haw.', preamble: 'We, the people of Hawaii, grateful for Divine Guidance, and mindful of our Hawaiian heritage, do hereby ordain and establish this constitution for the State of Hawaii.', billOfRights: 'All persons are free by nature and are equal in their inherent and inalienable rights. Among these rights are the enjoyment of life, liberty and the pursuit of happiness, and the acquiring and possessing of property.' },
    { id: 'id', abbr: 'Idaho', preamble: 'We, the people of the State of Idaho, grateful to Almighty God for our freedom, do establish this Constitution.', billOfRights: 'All men are by nature free and equal, and have certain inalienable rights, among which are enjoying and defending life and liberty; acquiring, possessing and protecting property.' },
    { id: 'il', abbr: 'Ill.', preamble: 'We, the People of the State of Illinois - grateful to Almighty God for the civil, political and religious liberty which He has permitted us to enjoy - do ordain and establish this Constitution for the State of Illinois.', billOfRights: 'All men are by nature free and independent and have certain inherent and inalienable rights among which are life, liberty and the pursuit of happiness.' },
    { id: 'in', abbr: 'Ind.', preamble: 'To the end that justice be established, public order maintained, and liberty perpetuated: We, the people of the State of Indiana, do ordain this Constitution.', billOfRights: 'We declare, that all people are created equal; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty, and the pursuit of happiness.' },
    { id: 'ia', abbr: 'Iowa', preamble: 'We, the People of the State of Iowa, grateful to the Supreme Being for the blessings hitherto enjoyed, do ordain and establish a free and independent government.', billOfRights: 'All men and women are, by nature, free and equal, and have certain inalienable rights—among which are those of enjoying and defending life and liberty, acquiring, possessing and protecting property, and pursuing and obtaining safety and happiness.' },
    { id: 'ks', abbr: 'Kan.', preamble: 'We, the people of Kansas, grateful to Almighty God for our civil and religious privileges, do ordain and establish this constitution.', billOfRights: 'All men are possessed of equal and inalienable natural rights, among which are life, liberty, and the pursuit of happiness.' },
    { id: 'ky', abbr: 'Ky.', preamble: 'We, the people of the Commonwealth of Kentucky, grateful to Almighty God for the civil, political and religious liberties we enjoy, do ordain and establish this Constitution.', billOfRights: 'All men are, by nature, free and equal, and have certain inherent and inalienable rights, among which may be reckoned: First: The right of enjoying and defending their lives and liberties.' },
    { id: 'la', abbr: 'La.', preamble: 'We, the people of Louisiana, grateful to Almighty God for the civil, political, economic, and religious liberties we enjoy, do ordain and establish this constitution.', billOfRights: 'All persons are born free and equal and have certain natural, inherent, and inalienable rights; among these are life, liberty, and the pursuit of happiness. No person shall be deprived of life, liberty, or property, except by due process of law.' },
    { id: 'me', abbr: 'Me.', preamble: 'We the people of Maine, acknowledging with grateful hearts the goodness of the Sovereign Ruler of the Universe, do ordain and establish the following Constitution.', billOfRights: 'All people are born equally free and independent, and have certain natural, inherent and unalienable rights, among which are those of enjoying and defending life and liberty, acquiring, possessing and protecting property, and of pursuing and obtaining safety and happiness.' },
    { id: 'md', abbr: 'Md.', preamble: 'We, the People of the State of Maryland, grateful to Almighty God for our civil and religious liberty, declare.', billOfRights: 'That all Government of right originates from the People, is founded in compact only, and instituted solely for the good of the whole; and they have, at all times, the inalienable right to alter, reform or abolish their Form of Government.' },
    { id: 'ma', abbr: 'Mass.', preamble: 'The body politic is formed by a voluntary association of individuals: it is a social compact, by which the whole people covenants with each citizen for the common good.', billOfRights: 'All people are born free and equal and have certain natural, essential and unalienable rights; among which may be reckoned the right of enjoying and defending their lives and liberties.' },
    { id: 'mi', abbr: 'Mich.', preamble: 'We, the people of the State of Michigan, grateful to Almighty God for the blessings of freedom, do ordain and establish this constitution.', billOfRights: 'All political power is inherent in the people. Government is instituted for their equal benefit, security and protection.' },
    { id: 'mn', abbr: 'Minn.', preamble: 'We, the people of the state of Minnesota, grateful to God for our civil and religious liberty, do ordain and establish this Constitution.', billOfRights: 'Government is instituted for the security, benefit and protection of the people, in whom all political power is inherent, together with the right to alter, modify or reform government whenever required by the public good.' },
    { id: 'ms', abbr: 'Miss.', preamble: 'We, the people of Mississippi in convention assembled, grateful to Almighty God, do ordain and establish this Constitution.', billOfRights: 'All political power is inherent in the people, and all free governments are founded on their authority, and established for their benefit.' },
    { id: 'mo', abbr: 'Mo.', preamble: 'We, the people of Missouri, with profound reverence for the Supreme Ruler of the Universe, do establish this constitution for the better government of the state.', billOfRights: 'That all political power is vested in and derived from the people; that all government of right originates from the people, is founded upon their will only, and is instituted solely for the good of the whole.' },
    { id: 'mt', abbr: 'Mont.', preamble: 'We the people of Montana grateful to God for the quiet beauty of our state, the grandeur of our mountains, the vastness of our rolling plains, do ordain and establish this constitution.', billOfRights: 'All persons are born free and have certain inalienable rights. They include the right to a clean and healthful environment and the rights of pursuing life\'s basic necessities, enjoying and defending their lives and liberties, acquiring, possessing and protecting property, and seeking their safety, health and happiness in all lawful ways.' },
    { id: 'ne', abbr: 'Neb.', preamble: 'We, the people, grateful to Almighty God for our freedom, do ordain and establish the following declaration of rights and frame of government.', billOfRights: 'All persons are by nature free and independent, and have certain inherent and inalienable rights; among these are life, liberty, the pursuit of happiness, and the right to keep and bear arms for security or defense of self, family, home, and others, and for lawful common defense, hunting, recreational use, and all other lawful purposes.' },
    { id: 'nv', abbr: 'Nev.', preamble: 'We the people of the State of Nevada, Grateful to Almighty God for our freedom, do establish this Constitution.', billOfRights: 'All men are by Nature free and equal and have certain inalienable rights among which are those of enjoying and defending life and liberty; Acquiring, Possessing and Protecting property and pursuing and obtaining safety and happiness.' },
    { id: 'nh', abbr: 'N.H.', preamble: 'The people inhabiting the territory formerly called the province of New Hampshire, do hereby solemnly agree to form themselves into a free, sovereign and independent State.', billOfRights: 'All men are born equally free and independent; therefore, all government of right originates from the people, is founded in consent, and instituted for the general good.' },
    { id: 'nj', abbr: 'N.J.', preamble: 'We, the people of the State of New Jersey, grateful to Almighty God for the civil and religious liberty which He hath so long permitted us to enjoy, do ordain and establish this Constitution.', billOfRights: 'All persons are by nature free and independent, and have certain natural and unalienable rights, among which are those of enjoying and defending life and liberty, of acquiring, possessing, and protecting property, and of pursuing and obtaining safety and happiness.' },
    { id: 'nm', abbr: 'N.M.', preamble: 'We, the people of New Mexico, grateful to Almighty God for the blessings of liberty, do ordain and establish this constitution.', billOfRights: 'All persons are born equally free, and have certain natural, inherent and inalienable rights, among which are the rights of enjoying and defending life and liberty, of acquiring, possessing and protecting property, and of seeking and obtaining safety and happiness.' },
    { id: 'ny', abbr: 'N.Y.', preamble: 'We, the people of the State of New York, grateful to Almighty God for our Freedom, do establish this Constitution.', billOfRights: 'No member of this state shall be disfranchised, or deprived of any of the rights or privileges secured to any citizen thereof, unless by the law of the land, or the judgment of his or her peers.' },
    { id: 'nc', abbr: 'N.C.', preamble: 'We, the people of the State of North Carolina, grateful to Almighty God, the Sovereign Ruler of Nations, do ordain and establish this Constitution.', billOfRights: 'We hold it to be self-evident that all persons are created equal; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty, the enjoyment of the fruits of their own labor, and the pursuit of happiness.' },
    { id: 'nd', abbr: 'N.D.', preamble: 'We, the people of North Dakota, grateful to Almighty God for the blessings of civil and religious liberty, do ordain and establish this constitution.', billOfRights: 'All individuals are by nature equally free and independent and have certain inalienable rights, among which are those of enjoying and defending life and liberty; acquiring, possessing and protecting property and reputation; pursuing and obtaining safety and happiness; and to keep and bear arms for the defense of their person, family, property, and the state, and for lawful hunting, recreational, and other lawful purposes.' },
    { id: 'oh', abbr: 'Ohio', preamble: 'We, the people of the State of Ohio, grateful to Almighty God for our freedom, do establish this Constitution.', billOfRights: 'All people are, by nature, free and independent, and have certain inalienable rights, among which are those of enjoying and defending life and liberty, acquiring, possessing, and protecting property, and seeking and obtaining happiness and safety.' },
    { id: 'ok', abbr: 'Okla.', preamble: 'Invoking the guidance of Almighty God, in order to secure and perpetuate the blessing of liberty, we, the people of the State of Oklahoma, do ordain and establish this Constitution.', billOfRights: 'All persons have the inherent right to life, liberty, the pursuit of happiness, and the enjoyment of the gains of their own industry.' },
    { id: 'or', abbr: 'Or.', preamble: 'We the people of the State of Oregon to the end that Justice be established, order maintained, and liberty perpetuated, do ordain this Constitution.', billOfRights: 'We declare that all men, when they form a social compact are equal in right: that all power is inherent in the people, and all free governments are founded on their authority, and instituted for their peace, safety, and happiness.' },
    { id: 'pa', abbr: 'Pa.', preamble: 'We, the people of the Commonwealth of Pennsylvania, grateful to Almighty God for the blessings of civil and religious liberty, do ordain and establish this Constitution.', billOfRights: 'All men are born equally free and independent, and have certain inherent and indefeasible rights, among which are those of enjoying and defending life and liberty, of acquiring, possessing and protecting property and reputation, and of pursuing their own happiness.' },
    { id: 'ri', abbr: 'R.I.', preamble: 'We, the people of the State of Rhode Island and Providence Plantations, grateful to Almighty God for the civil and religious liberty, do ordain and establish this Constitution.', billOfRights: 'In the words of the Father of his Country, we declare that "the basis of our political systems is the right of the people to make and alter their constitutions of government."' },
    { id: 'sc', abbr: 'S.C.', preamble: 'We, the people of the State of South Carolina, grateful to God for our liberties, do ordain and establish this Constitution.', billOfRights: 'All political power is vested in and derived from the people only, therefore, they have the right at all times to modify their form of government.' },
    { id: 'sd', abbr: 'S.D.', preamble: 'We, the people of South Dakota, grateful to Almighty God for our civil and religious liberties, do ordain and establish this Constitution.', billOfRights: 'All men are born equally free and independent, and have certain inherent rights, among which are those of enjoying and defending life and liberty, of acquiring and protecting property and the pursuit of happiness.' },
    { id: 'tn', abbr: 'Tenn.', preamble: 'That all power is inherent in the people, and all free governments are founded on their authority, and instituted for their peace, safety, and happiness.', billOfRights: 'That all power is inherent in the people, and all free governments are founded on their authority, and instituted for their peace, safety, and happiness; for the advancement of those ends they have at all times, an unalienable and indefeasible right to alter, reform, or abolish the government in such manner as they may think proper.' },
    { id: 'tx', abbr: 'Tex.', preamble: 'Humbly invoking the blessings of Almighty God, the people of the State of Texas, do ordain and establish this Constitution.', billOfRights: 'All free men, when they form a social compact, have equal rights, and no man, or set of men, is entitled to exclusive separate public emoluments, or privileges, but in consideration of public services.' },
    { id: 'ut', abbr: 'Utah', preamble: 'Grateful to Almighty God for life and liberty, we, the people of Utah, do ordain and establish this Constitution.', billOfRights: 'All men have the inherent and inalienable right to enjoy and defend their lives and liberties; to acquire, possess and protect property; to worship according to the dictates of their consciences; to assemble peaceably, protest against wrongs, and petition for redress of grievances; to communicate freely their thoughts and opinions, being responsible for the abuse of that right.' },
    { id: 'vt', abbr: 'Vt.', preamble: 'That all persons are born equally free and independent, and have certain natural, inherent, and unalienable rights.', billOfRights: 'That all persons are born equally free and independent, and have certain natural, inherent, and unalienable rights, amongst which are the enjoying and defending life and liberty, acquiring, possessing and protecting property, and pursuing and obtaining happiness and safety.' },
    { id: 'va', abbr: 'Va.', preamble: 'We, the people of Virginia, do ordain and establish this Constitution.', billOfRights: 'That all men are by nature equally free and independent and have certain inherent rights, of which, when they enter into a state of society, they cannot, by any compact, deprive or divest their posterity; namely, the enjoyment of life and liberty, with the means of acquiring and possessing property, and pursuing and obtaining happiness and safety.' },
    { id: 'wa', abbr: 'Wash.', preamble: 'We, the people of the State of Washington, grateful to the Supreme Ruler of the Universe for our liberties, do ordain this constitution.', billOfRights: 'All political power is inherent in the people, and governments derive their just powers from the consent of the governed, and are established to protect and maintain individual rights.' },
    { id: 'wv', abbr: 'W. Va.', preamble: 'Since through Divine Providence we enjoy the blessings of civil, political and religious liberty, we, the people of West Virginia, do establish this Constitution.', billOfRights: 'All men are, by nature, equally free and independent, and have certain inherent rights, of which, when they enter into a state of society, they cannot by any compact deprive or divest their posterity, namely: the enjoyment of life and liberty, with the means of acquiring and possessing property, and of pursuing and obtaining happiness and safety.' },
    { id: 'wi', abbr: 'Wis.', preamble: 'We, the people of Wisconsin, grateful to Almighty God for our freedom, do establish this constitution.', billOfRights: 'All people are born equally free and independent, and have certain inherent rights; among these are life, liberty and the pursuit of happiness; to secure these rights, governments are instituted, deriving their just powers from the consent of the governed.' },
    { id: 'wy', abbr: 'Wyo.', preamble: 'We, the people of the State of Wyoming, grateful to God for our civil, political and religious liberties, do ordain and establish this Constitution.', billOfRights: 'All power is inherent in the people, and all free governments are founded on their authority, and instituted for their peace, safety and happiness; for the advancement of these ends they have at all times an inalienable and indefeasible right to alter, reform or abolish the government in such manner as they may think proper.' }
  ]
  
  const sections: Section[] = []
  
  stateData.forEach((state, idx) => {
    sections.push(
      {
        id: `${state.id}-const-preamble`,
        documentId: `${state.id}-constitution`,
        title: 'Preamble',
        number: 'Preamble',
        text: state.preamble,
        canonicalCitation: `${state.abbr} Const. pmbl.`,
        order: idx * 100
      },
      {
        id: `${state.id}-const-art1-s1`,
        documentId: `${state.id}-constitution`,
        title: 'Bill of Rights - Fundamental Rights',
        number: 'I.1',
        text: state.billOfRights,
        canonicalCitation: `${state.abbr} Const. art. I, § 1`,
        order: idx * 100 + 1
      },
      {
        id: `${state.id}-const-art1-s2`,
        documentId: `${state.id}-constitution`,
        title: 'Bill of Rights - Freedom of Religion',
        number: 'I.2',
        text: 'All persons shall have the right to worship Almighty God according to the dictates of their own conscience. No person shall be compelled to attend, erect or support any place of worship, or maintain any form of worship, against his or her consent. No religious test shall ever be required as a qualification to any office or public trust under this State.',
        canonicalCitation: `${state.abbr} Const. art. I, § 2`,
        order: idx * 100 + 2
      },
      {
        id: `${state.id}-const-art1-s3`,
        documentId: `${state.id}-constitution`,
        title: 'Bill of Rights - Freedom of Speech and Press',
        number: 'I.3',
        text: 'Every person may freely speak, write and publish on all subjects, being responsible for the abuse of that liberty. No law shall be passed to restrain or abridge the liberty of speech or of the press.',
        canonicalCitation: `${state.abbr} Const. art. I, § 3`,
        order: idx * 100 + 3
      },
      {
        id: `${state.id}-const-art1-s4`,
        documentId: `${state.id}-constitution`,
        title: 'Bill of Rights - Due Process',
        number: 'I.4',
        text: 'No person shall be deprived of life, liberty, or property, without due process of law.',
        canonicalCitation: `${state.abbr} Const. art. I, § 4`,
        order: idx * 100 + 4
      },
      {
        id: `${state.id}-const-art2`,
        documentId: `${state.id}-constitution`,
        title: 'Article II - Legislative Power',
        number: 'II',
        text: 'The legislative power of this State shall be vested in a Legislature, which shall consist of a Senate and a House of Representatives.',
        canonicalCitation: `${state.abbr} Const. art. II`,
        order: idx * 100 + 10
      },
      {
        id: `${state.id}-const-art3`,
        documentId: `${state.id}-constitution`,
        title: 'Article III - Executive Power',
        number: 'III',
        text: 'The supreme executive power of this State is vested in the Governor, who shall see that the law is faithfully executed.',
        canonicalCitation: `${state.abbr} Const. art. III`,
        order: idx * 100 + 20
      },
      {
        id: `${state.id}-const-local-govt`,
        documentId: `${state.id}-constitution`,
        title: 'Local Government',
        number: 'Local Govt',
        text: 'Counties and municipalities may exercise local powers of government, subject to the general laws of this State.',
        canonicalCitation: `${state.abbr} Const. (Local Government)`,
        order: idx * 100 + 30
      }
    )
  })
  
  return sections
}

export const sections: Section[] = [
  // ── Complete U.S. Constitution (all Articles + all 27 Amendments) ──
  ...usConstitutionSections,
  // ── State Constitution Sections ──
  // NOTE: Preambles and Art. I §1 contain actual state-specific text.
  // Sections I.2, I.3, I.4, Art II, Art III, and Local Govt use representative
  // language typical of state constitutions. Users should verify against the
  // official source URL for each state's constitution.
  ...stateConstitutionSections(),
  {
    id: 'civil-rights-act-title-vii',
    documentId: 'civil-rights-act-1964',
    title: 'Title VII - Equal Employment Opportunity',
    number: 'VII',
    text: 'It shall be an unlawful employment practice for an employer to fail or refuse to hire or to discharge any individual, or otherwise to discriminate against any individual with respect to his compensation, terms, conditions, or privileges of employment, because of such individual\'s race, color, religion, sex, or national origin.',
    canonicalCitation: '42 U.S.C. § 2000e-2(a)(1)',
    order: 7
  },
  {
    id: 'voting-rights-act-s2',
    documentId: 'voting-rights-act-1965',
    title: 'Section 2 - Prohibition Against Voting Discrimination',
    number: '2',
    text: 'No voting qualification or prerequisite to voting or standard, practice, or procedure shall be imposed or applied by any State or political subdivision in a manner which results in a denial or abridgement of the right of any citizen of the United States to vote on account of race or color.',
    canonicalCitation: '52 U.S.C. § 10301',
    order: 2
  },
  {
    id: 'ada-title-i',
    documentId: 'ada-1990',
    title: 'Title I - Employment',
    number: 'I',
    text: 'No covered entity shall discriminate against a qualified individual on the basis of disability in regard to job application procedures, the hiring, advancement, or discharge of employees, employee compensation, job training, and other terms, conditions, and privileges of employment.',
    canonicalCitation: '42 U.S.C. § 12112(a)',
    order: 1
  },
  {
    id: 'foia-disclosure',
    documentId: 'foia',
    title: 'Section 552(a) - Public Disclosure',
    number: '552(a)',
    text: 'Each agency shall make available to the public information as follows: (1) Each agency shall separately state and currently publish in the Federal Register for the guidance of the public— (A) descriptions of its central and field organization and the established places at which, the employees from whom, and the methods whereby, the public may obtain information, make submittals or requests, or obtain decisions...',
    canonicalCitation: '5 U.S.C. § 552(a)',
    order: 1
  },
  {
    id: 'usc-18-241',
    documentId: 'usc-title-18',
    title: 'Section 241 - Conspiracy Against Rights',
    number: '241',
    text: 'If two or more persons conspire to injure, oppress, threaten, or intimidate any person in any State, Territory, Commonwealth, Possession, or District in the free exercise or enjoyment of any right or privilege secured to him by the Constitution or laws of the United States, or because of his having so exercised the same; or if two or more persons go in disguise on the highway, or on the premises of another, with intent to prevent or hinder his free exercise or enjoyment of any right or privilege so secured— They shall be fined under this title or imprisoned not more than ten years, or both.',
    canonicalCitation: '18 U.S.C. § 241',
    order: 241
  },
  {
    id: 'treaty-un-charter-art1',
    documentId: 'treaty-un-charter',
    title: 'Article 1 - Purposes of the United Nations',
    number: '1',
    text: 'The Purposes of the United Nations are: 1. To maintain international peace and security, and to that end: to take effective collective measures for the prevention and removal of threats to the peace, and for the suppression of acts of aggression or other breaches of the peace, and to bring about by peaceful means, and in conformity with the principles of justice and international law, adjustment or settlement of international disputes or situations which might lead to a breach of the peace...',
    canonicalCitation: 'U.N. Charter art. 1',
    order: 1
  },
  {
    id: 'treaty-udhr-art1',
    documentId: 'treaty-udhr',
    title: 'Article 1 - Right to Equality',
    number: '1',
    text: 'All human beings are born free and equal in dignity and rights. They are endowed with reason and conscience and should act towards one another in a spirit of brotherhood.',
    canonicalCitation: 'UDHR art. 1',
    order: 1
  },
  {
    id: 'treaty-udhr-art3',
    documentId: 'treaty-udhr',
    title: 'Article 3 - Right to Life, Liberty, Personal Security',
    number: '3',
    text: 'Everyone has the right to life, liberty and security of person.',
    canonicalCitation: 'UDHR art. 3',
    order: 3
  },
  {
    id: 'treaty-udhr-art19',
    documentId: 'treaty-udhr',
    title: 'Article 19 - Freedom of Opinion and Information',
    number: '19',
    text: 'Everyone has the right to freedom of opinion and expression; this right includes freedom to hold opinions without interference and to seek, receive and impart information and ideas through any media and regardless of frontiers.',
    canonicalCitation: 'UDHR art. 19',
    order: 19
  }
]

export const learningTopics: LearningModule[] = [
  {
    id: 'supremacy-clause',
    title: 'The Supremacy Clause',
    category: 'Constitutional Framework',
    description: 'Understand how the Supremacy Clause establishes the hierarchy of law in the United States.',
    content: `The Supremacy Clause, found in Article VI, Clause 2 of the U.S. Constitution, establishes that federal law is "the supreme Law of the Land." This means that when state or local laws conflict with valid federal law, the federal law prevails.

**Primary Text:**
"This Constitution, and the Laws of the United States which shall be made in Pursuance thereof; and all Treaties made, or which shall be made, under the Authority of the United States, shall be the supreme Law of the Land..." (U.S. Const. art. VI, cl. 2)

**What This Means:**
The hierarchy of U.S. law follows this order (from highest to lowest authority):
1. U.S. Constitution
2. Federal statutes and treaties
3. Federal regulations
4. State constitutions
5. State statutes
6. State regulations
7. Local ordinances

**Important Limitation:**
Federal law only preempts state/local law in areas where Congress has constitutional authority to act. The Tenth Amendment reserves powers not delegated to the federal government to the states or the people.`,
    relatedSectionIds: ['us-const-art6', 'us-const-amend10'],
    order: 1,
  },
  {
    id: 'preemption-types',
    title: 'Types of Federal Preemption',
    category: 'Constitutional Framework',
    description: 'Learn how federal law can preempt state and local law through express, conflict, and field preemption.',
    content: `Federal preemption occurs when federal law takes precedence over state or local law. There are several types:

**1. Express Preemption**
Congress explicitly states in a statute that federal law preempts state law in a particular area.

**2. Implied Preemption – Field Preemption**
Federal regulation is so comprehensive that it occupies the entire field, leaving no room for state law (e.g., immigration law).

**3. Implied Preemption – Conflict Preemption**
State law directly conflicts with federal law, making it impossible to comply with both, or state law obstructs federal objectives.

**Example (Hypothetical for Educational Purposes):**
If a state passes a law requiring food labels that conflict with FDA labeling requirements, the state law would likely be preempted under conflict preemption doctrine.

**Note:** This is educational information, not legal advice. Actual preemption analysis requires examining specific statutes, regulations, and case law.`,
    relatedSectionIds: ['us-const-art6'],
    order: 2,
  },
  {
    id: 'incorporation',
    title: 'Incorporation Doctrine',
    category: 'Constitutional Rights',
    description: 'How the Bill of Rights became applicable to state governments through the Fourteenth Amendment.',
    content: `The Incorporation Doctrine is the legal principle by which the Bill of Rights (the first ten amendments to the U.S. Constitution) applies to state and local governments, not just the federal government.

**Constitutional Basis:**
The Fourteenth Amendment's Due Process Clause: "...nor shall any State deprive any person of life, liberty, or property, without due process of law..." (U.S. Const. amend. XIV, § 1)

**How It Works:**
Through Supreme Court decisions over many decades, most provisions of the Bill of Rights have been "incorporated" and made applicable to states. This means states cannot violate fundamental rights like freedom of speech, freedom of religion, protection against unreasonable searches, etc.

**Practical Impact:**
State constitutions and laws must respect these federal constitutional minimums, though states may provide greater protections under their own constitutions.`,
    relatedSectionIds: ['us-const-amend14', 'us-const-amend1', 'us-const-amend4'],
    order: 3,
  },
  {
    id: 'federalism',
    title: 'Federalism',
    category: 'Constitutional Framework',
    description: 'The division of governmental power between the federal government and the states.',
    content: `Federalism is the constitutional system that divides governmental power between the national (federal) government and the state governments.

**Constitutional Foundation:**
The U.S. Constitution enumerates specific powers for the federal government (Article I, Section 8) and reserves all other powers to the states or the people (Tenth Amendment).

**Key Principles:**
1. **Enumerated Powers**: The federal government possesses only those powers specifically granted by the Constitution.
2. **Reserved Powers**: Powers not delegated to the federal government are reserved to the states (U.S. Const. amend. X).
3. **Concurrent Powers**: Some powers (like taxation) are shared between federal and state governments.
4. **Supremacy**: When federal and state law conflict on a matter within federal authority, federal law prevails (U.S. Const. art. VI, cl. 2).

**Practical Significance:**
Federalism means that Americans live under two sets of laws — federal and state — each operating within its constitutional sphere. State constitutions are the supreme law within their state, subject to the U.S. Constitution.`,
    relatedSectionIds: ['us-const-amend10', 'us-const-art1-s8', 'us-const-art6'],
    order: 4,
  },
  {
    id: 'checks-and-balances',
    title: 'Checks and Balances',
    category: 'Constitutional Framework',
    description: 'How the three branches of government limit each other\'s power.',
    content: `The system of checks and balances ensures that no single branch of the federal government becomes too powerful. Each branch has specific powers to check the other two.

**The Three Branches:**
1. **Legislative (Congress)** — Makes laws (U.S. Const. art. I)
2. **Executive (President)** — Enforces laws (U.S. Const. art. II)
3. **Judicial (Courts)** — Interprets laws (U.S. Const. art. III)

**Key Checks:**
- Congress can override a presidential veto with a two-thirds vote
- The President can veto legislation passed by Congress
- The Supreme Court can declare laws unconstitutional (judicial review)
- The Senate confirms presidential appointments (U.S. Const. art. II, § 2)
- Congress can impeach and remove the President or federal judges (U.S. Const. art. I, § 2–3; art. II, § 4)
- The President nominates federal judges

**Purpose:**
James Madison wrote in Federalist No. 51: "Ambition must be made to counteract ambition." The system prevents tyranny by ensuring power is distributed and each branch can limit the others.`,
    relatedSectionIds: ['us-const-art1', 'us-const-art2', 'us-const-art3', 'us-const-art2-s4'],
    order: 5,
  },
  {
    id: 'treaty-power',
    title: 'The Treaty Power',
    category: 'Federal Authority',
    description: 'How treaties are made, their legal force, and their place in the hierarchy of law.',
    content: `Under the U.S. Constitution, the President has the power to make treaties with foreign nations, subject to the advice and consent of the Senate.

**Constitutional Text:**
"He shall have Power, by and with the Advice and Consent of the Senate, to make Treaties, provided two thirds of the Senators present concur." (U.S. Const. art. II, § 2)

**Legal Status of Treaties:**
Treaties are part of "the supreme Law of the Land" under the Supremacy Clause (U.S. Const. art. VI, cl. 2). This means:
- Ratified treaties have the same legal force as federal statutes
- Treaties can preempt conflicting state laws
- When a treaty and a federal statute conflict, the later-in-time rule generally applies

**Self-Executing vs. Non-Self-Executing Treaties:**
- **Self-executing treaties** take effect as domestic law immediately upon ratification
- **Non-self-executing treaties** require implementing legislation from Congress before they can be enforced in U.S. courts

**Important Note:**
The U.S. has ratified some international agreements with reservations, declarations, or understandings that may limit their domestic application. Treaty status information on this platform notes these where applicable.`,
    relatedSectionIds: ['us-const-art2-s2', 'us-const-art6'],
    order: 6,
  },
  {
    id: 'home-rule',
    title: 'Home Rule',
    category: 'State & Local Authority',
    description: 'How local governments derive and exercise their authority under state constitutions.',
    content: `Home rule is the power of a local government (city, county, or municipality) to set up its own system of self-governance without receiving a charter from the state legislature.

**Constitutional Basis:**
Local governments are creatures of state law. Their authority derives from the state constitution and state statutes, not directly from the U.S. Constitution. Many state constitutions include "home rule" provisions that grant local governments varying degrees of self-governance authority.

**Types of Home Rule:**
1. **Structural Home Rule**: Power to adopt or amend a local charter (organizational structure)
2. **Functional Home Rule**: Power to exercise broad local government functions
3. **Fiscal Home Rule**: Power to raise revenue through taxes, fees, and borrowing

**Dillon's Rule vs. Home Rule:**
- **Dillon's Rule** (traditional): Local governments can exercise only those powers expressly granted by the state legislature
- **Home Rule**: Local governments may exercise any power not specifically denied by the state constitution or statute

**Limits:**
Even with home rule, local governments remain subject to:
- The U.S. Constitution
- Federal law
- Their state's constitution
- State statutes (where applicable)`,
    relatedSectionIds: ['us-const-amend10'],
    order: 7,
  },
  {
    id: 'due-process',
    title: 'Due Process of Law',
    category: 'Constitutional Rights',
    description: 'The constitutional guarantee that government must follow fair procedures before depriving individuals of life, liberty, or property.',
    content: `Due process is guaranteed by two provisions of the U.S. Constitution:

**Fifth Amendment** (applies to the federal government):
"No person shall be...deprived of life, liberty, or property, without due process of law." (U.S. Const. amend. V)

**Fourteenth Amendment** (applies to state and local governments):
"...nor shall any State deprive any person of life, liberty, or property, without due process of law." (U.S. Const. amend. XIV, § 1)

**Two Types of Due Process:**

1. **Procedural Due Process**: The government must follow fair procedures before taking action against an individual. This typically includes:
   - Notice of the government's intended action
   - An opportunity to be heard
   - A neutral decision-maker

2. **Substantive Due Process**: Certain fundamental rights are so important that the government cannot infringe upon them regardless of what procedures are used. Courts strictly scrutinize government actions that affect fundamental rights such as:
   - Right to privacy
   - Right to marry
   - Right to travel
   - Parental rights

**State Constitutional Parallels:**
Nearly every state constitution contains its own due process clause. State courts may interpret their state's due process protections more broadly than the federal minimum.`,
    relatedSectionIds: ['us-const-amend5', 'us-const-amend14'],
    order: 8,
  },
]
