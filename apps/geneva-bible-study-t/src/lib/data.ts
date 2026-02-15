import { TranslationEdition, TextWork, HistoricalEvent, VerseUnit } from './types'

export const translations: TranslationEdition[] = [
  {
    id: 'geneva',
    name: 'Geneva Bible',
    shortCode: 'GNV',
    year: 1560,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['William Whittingham', 'Miles Coverdale', 'Christopher Goodman', 'Anthony Gilby', 'Thomas Sampson'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus', 'Tyndale Translation'],
    revisionLineage: ['Tyndale (1526)', 'Great Bible (1539)', 'Geneva (1560)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'The Geneva Bible was the Bible of the Protestant Reformation, featuring extensive marginal notes that explained Reformed theology. It was the primary English Bible for English-speaking Protestants until the King James Version gained popularity. Known for its scholarly accuracy and clear language, it was the Bible brought to America by the Pilgrims.',
    languageCode: 'en'
  },
  {
    id: 'kjv',
    name: 'King James Version',
    shortCode: 'KJV',
    year: 1611,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['47 scholars in six committees'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus', 'Bishops\' Bible'],
    revisionLineage: ['Tyndale (1526)', 'Bishops\' Bible (1568)', 'KJV (1611)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'Commissioned by King James I, the KJV became the most influential English Bible translation. Its majestic prose and poetic language shaped English literature for centuries. Created to replace the Geneva Bible and unify the Church of England, it avoided controversial marginal notes.',
    languageCode: 'en'
  },
  {
    id: 'web',
    name: 'World English Bible',
    shortCode: 'WEB',
    year: 2000,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Rainbow Missions'],
    sourceTexts: ['Hebrew Biblia Hebraica Stuttgartensia', 'Greek Majority Text'],
    revisionLineage: ['American Standard Version (1901)', 'WEB (2000)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'A modern English translation in the public domain, based on the American Standard Version. Uses contemporary English while maintaining formal equivalence to the original texts.',
    languageCode: 'en'
  },
  {
    id: 'ylt',
    name: "Young's Literal Translation",
    shortCode: 'YLT',
    year: 1862,
    philosophy: 'formal-equivalence',
    philosophyScore: 1,
    editors: ['Robert Young'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus'],
    revisionLineage: ['YLT (1862)', 'YLT Revised (1887)', 'YLT Third Edition (1898)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: "An extremely literal translation that attempts to preserve the tense and word usage of the original languages. Created by Robert Young, scholar and compiler of Young's Analytical Concordance.",
    languageCode: 'en'
  },
  {
    id: 'asv',
    name: 'American Standard Version',
    shortCode: 'ASV',
    year: 1901,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['American Revision Committee'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus'],
    revisionLineage: ['KJV (1611)', 'RV (1885)', 'ASV (1901)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'American revision of the English Revised Version, seeking to improve accuracy while maintaining the dignity of the KJV tradition. Known for its scholarly precision.',
    languageCode: 'en'
  },
  {
    id: 'basicenglish',
    name: 'Bible in Basic English',
    shortCode: 'BBE',
    year: 1949,
    philosophy: 'dynamic-equivalence',
    philosophyScore: 6,
    editors: ['S. H. Hooke'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Critical Text'],
    revisionLineage: ['BBE (1949)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'Translated using only 850 basic English words plus 100 special Bible words. Designed for those learning English or seeking simple, clear language.',
    languageCode: 'en'
  },
  {
    id: 'darby',
    name: 'Darby Translation',
    shortCode: 'DARBY',
    year: 1890,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['John Nelson Darby'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Critical Text'],
    revisionLineage: ['Darby (1890)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'Created by John Nelson Darby, founder of the Plymouth Brethren movement. Known for careful attention to verb tenses and theological precision.',
    languageCode: 'en'
  },
  {
    id: 'douayrheims',
    name: 'Douay-Rheims Bible',
    shortCode: 'DRA',
    year: 1609,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['English College, Douai'],
    sourceTexts: ['Latin Vulgate'],
    revisionLineage: ['Latin Vulgate (405)', 'Douay-Rheims (1609)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'The official English Bible of the Catholic Church for centuries, translated from the Latin Vulgate. Includes the Deuterocanonical books (Apocrypha).',
    languageCode: 'en'
  },
  {
    id: 'webster',
    name: "Webster's Bible",
    shortCode: 'WBT',
    year: 1833,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Noah Webster'],
    sourceTexts: ['KJV'],
    revisionLineage: ['KJV (1611)', 'Webster (1833)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'A revision of the KJV by Noah Webster (of dictionary fame), updating archaic language and correcting perceived errors while maintaining the KJV style.',
    languageCode: 'en'
  },
  {
    id: 'akjv',
    name: 'American King James Version',
    shortCode: 'AKJV',
    year: 1999,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Michael Phelps'],
    sourceTexts: ['KJV'],
    revisionLineage: ['KJV (1611)', 'AKJV (1999)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'An updated version of the KJV using modern American spelling and punctuation, placed in the public domain for free use.',
    languageCode: 'en'
  },
  {
    id: 'leb',
    name: 'Lexham English Bible',
    shortCode: 'LEB',
    year: 2012,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Lexham Press'],
    sourceTexts: ['Hebrew Biblia Hebraica Stuttgartensia', 'Greek Nestle-Aland 28'],
    revisionLineage: ['LEB (2012)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'A modern literal translation designed to be used with Logos Bible Software, emphasizing transparency to the original languages.',
    languageCode: 'en'
  },
  {
    id: 'wb',
    name: 'World Messianic Bible',
    shortCode: 'WMB',
    year: 2014,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Rainbow Missions'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Majority Text'],
    revisionLineage: ['WEB (2000)', 'WMB (2014)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'Based on the World English Bible, using Messianic Jewish terminology and restoring Hebrew names and concepts.',
    languageCode: 'en'
  },
  {
    id: 'kjva',
    name: 'King James Version with Apocrypha',
    shortCode: 'KJVA',
    year: 1611,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['47 scholars in six committees'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus', 'Latin Vulgate'],
    revisionLineage: ['Tyndale (1526)', 'Bishops\' Bible (1568)', 'KJV (1611)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'The complete King James Version including the Deuterocanonical books (Apocrypha) originally included between the Old and New Testaments.',
    languageCode: 'en'
  },
  {
    id: 'clementine',
    name: 'Clementine Vulgate',
    shortCode: 'CLEMENTINE',
    year: 1592,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Pope Clement VIII'],
    sourceTexts: ['Original Latin Vulgate'],
    revisionLineage: ['Vulgate (405)', 'Clementine (1592)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'The official Latin text of the Catholic Church from 1592 to 1979. A revision of the Vulgate authorized by Pope Clement VIII.',
    languageCode: 'la'
  },
  {
    id: 'almeida',
    name: 'Almeida Revista e Corrigida',
    shortCode: 'ARC',
    year: 1898,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['João Ferreira de Almeida'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus'],
    revisionLineage: ['Almeida (1681)', 'ARC (1898)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'Classic Portuguese Bible translation, the first complete Portuguese Bible and still widely used by Portuguese-speaking Protestants.',
    languageCode: 'pt'
  },
  {
    id: 'rst',
    name: 'Russian Synodal Translation',
    shortCode: 'RST',
    year: 1876,
    philosophy: 'formal-equivalence',
    philosophyScore: 2,
    editors: ['Russian Bible Society'],
    sourceTexts: ['Hebrew Masoretic Text', 'Greek Textus Receptus', 'Septuagint'],
    revisionLineage: ['Church Slavonic (1751)', 'RST (1876)'],
    license: 'Public Domain',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: true
    },
    description: 'The standard Russian Bible translation, authorized by the Russian Orthodox Church and used by Russian-speaking Christians worldwide.',
    languageCode: 'ru'
  },
  {
    id: 'esv',
    name: 'English Standard Version',
    shortCode: 'ESV',
    year: 2001,
    philosophy: 'optimal-equivalence',
    philosophyScore: 3,
    editors: ['Translation Oversight Committee'],
    sourceTexts: ['Hebrew Biblia Hebraica Stuttgartensia', 'Greek Nestle-Aland 27/28', 'Septuagint'],
    revisionLineage: ['RSV (1952)', 'ESV (2001)'],
    license: 'Crossway Publishing',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: false,
      excerptLimit: 500
    },
    description: 'The ESV aims for word-for-word accuracy while maintaining literary quality. It stands in the Tyndale-King James tradition but uses modern critical Greek and Hebrew texts. Popular among evangelical scholars for study and teaching.',
    languageCode: 'en'
  },
  {
    id: 'niv',
    name: 'New International Version',
    shortCode: 'NIV',
    year: 1978,
    philosophy: 'dynamic-equivalence',
    philosophyScore: 5,
    editors: ['Committee on Bible Translation'],
    sourceTexts: ['Hebrew Biblia Hebraica', 'Greek Nestle-Aland', 'Septuagint'],
    revisionLineage: ['NIV (1978)', 'NIV (1984)', 'NIV (2011)'],
    license: 'Biblica',
    licenseRestrictions: {
      offlineAllowed: true,
      fullTextAllowed: false,
      excerptLimit: 500
    },
    description: 'The NIV uses dynamic equivalence to translate thoughts and ideas rather than word-for-word. It aims for natural contemporary English while remaining faithful to source texts. One of the most widely read modern English translations globally.',
    languageCode: 'en'
  }
]

export const bibleBooks: TextWork[] = [
  {
    id: 'gen',
    title: 'Genesis',
    shortName: 'Gen',
    category: 'law',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 50,
    compositionDate: '~1400-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Moses',
    introduction: 'Genesis opens the biblical library with primordial narratives of creation, early humanity, and the patriarchs Abraham, Isaac, Jacob, and Joseph. The book establishes foundational themes: God as creator, human rebellion, covenant promises, and divine redemption through a chosen people.',
    metadata: {
      testament: 'old',
      order: 1
    }
  },
  {
    id: 'exo',
    title: 'Exodus',
    shortName: 'Exod',
    category: 'law',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 40,
    compositionDate: '~1400-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Moses',
    introduction: 'Exodus narrates Israel\'s liberation from Egyptian slavery, the giving of the Law at Mount Sinai, and instructions for worship. Central to Jewish identity and Christian theology, it presents God as redeemer and lawgiver.',
    metadata: {
      testament: 'old',
      order: 2
    }
  },
  {
    id: 'lev',
    title: 'Leviticus',
    shortName: 'Lev',
    category: 'law',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 27,
    compositionDate: '~1400-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Moses',
    introduction: 'Leviticus contains laws for worship, sacrifice, purity, and holiness. It establishes the priestly system and moral code for Israel.',
    metadata: {
      testament: 'old',
      order: 3
    }
  },
  {
    id: 'num',
    title: 'Numbers',
    shortName: 'Num',
    category: 'law',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 36,
    compositionDate: '~1400-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Moses',
    introduction: 'Numbers chronicles Israel\'s wilderness wanderings, including census records, tribal organization, and rebellions against Moses and God.',
    metadata: {
      testament: 'old',
      order: 4
    }
  },
  {
    id: 'deu',
    title: 'Deuteronomy',
    shortName: 'Deut',
    category: 'law',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 34,
    compositionDate: '~1400-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Moses',
    introduction: 'Deuteronomy presents Moses\' final speeches to Israel before entering the Promised Land, restating the Law and calling for covenant faithfulness.',
    metadata: {
      testament: 'old',
      order: 5
    }
  },
  {
    id: 'jos',
    title: 'Joshua',
    shortName: 'Josh',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 24,
    compositionDate: '~600-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Joshua',
    introduction: 'Joshua narrates Israel\'s conquest and settlement of Canaan under Joshua\'s leadership after Moses\' death.',
    metadata: {
      testament: 'old',
      order: 6
    }
  },
  {
    id: 'jdg',
    title: 'Judges',
    shortName: 'Judg',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 21,
    compositionDate: '~600-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Samuel',
    introduction: 'Judges describes Israel\'s cycles of apostasy, oppression, and deliverance through military leaders called judges.',
    metadata: {
      testament: 'old',
      order: 7
    }
  },
  {
    id: 'rut',
    title: 'Ruth',
    shortName: 'Ruth',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 4,
    compositionDate: '~600-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Samuel',
    introduction: 'Ruth tells the story of a Moabite widow\'s loyalty to her Israelite mother-in-law and her inclusion in David\'s lineage.',
    metadata: {
      testament: 'old',
      order: 8
    }
  },
  {
    id: '1sa',
    title: '1 Samuel',
    shortName: '1 Sam',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 31,
    compositionDate: '~630-540 BCE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Samuel',
    introduction: '1 Samuel narrates the transition from judges to monarchy, featuring Samuel, Saul, and the rise of David.',
    metadata: {
      testament: 'old',
      order: 9
    }
  },
  {
    id: '2sa',
    title: '2 Samuel',
    shortName: '2 Sam',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 24,
    compositionDate: '~630-540 BCE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Samuel',
    introduction: '2 Samuel chronicles David\'s reign as king, including his successes, sins, and the succession crisis.',
    metadata: {
      testament: 'old',
      order: 10
    }
  },
  {
    id: 'psa',
    title: 'Psalms',
    shortName: 'Ps',
    category: 'wisdom',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 150,
    compositionDate: '~1000-300 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'David and others',
    introduction: 'Psalms is Israel\'s hymnal and prayer book, containing 150 poems expressing praise, lament, thanksgiving, and wisdom.',
    metadata: {
      testament: 'old',
      order: 19
    }
  },
  {
    id: 'pro',
    title: 'Proverbs',
    shortName: 'Prov',
    category: 'wisdom',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 31,
    compositionDate: '~950-700 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Solomon',
    introduction: 'Proverbs offers practical wisdom for daily living, emphasizing the fear of the Lord as the beginning of wisdom.',
    metadata: {
      testament: 'old',
      order: 20
    }
  },
  {
    id: 'isa',
    title: 'Isaiah',
    shortName: 'Isa',
    category: 'prophets',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 66,
    compositionDate: '~740-500 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Isaiah',
    introduction: 'Isaiah contains prophetic messages of judgment and hope, including messianic prophecies central to Christian theology.',
    metadata: {
      testament: 'old',
      order: 23
    }
  },
  {
    id: 'jer',
    title: 'Jeremiah',
    shortName: 'Jer',
    category: 'prophets',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 52,
    compositionDate: '~627-580 BCE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Jeremiah',
    introduction: 'Jeremiah prophesied Judah\'s exile, calling for repentance while promising future restoration and a new covenant.',
    metadata: {
      testament: 'old',
      order: 24
    }
  },
  {
    id: 'dan',
    title: 'Daniel',
    shortName: 'Dan',
    category: 'prophets',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 12,
    compositionDate: '~165 BCE or ~530 BCE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Daniel',
    introduction: 'Daniel combines narratives of Jewish faithfulness in Babylonian exile with apocalyptic visions of future kingdoms.',
    metadata: {
      testament: 'old',
      order: 27
    }
  },
  {
    id: 'mat',
    title: 'Matthew',
    shortName: 'Matt',
    category: 'gospels',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 28,
    compositionDate: '~70-90 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Matthew the Apostle',
    introduction: 'Matthew presents Jesus as the Jewish Messiah fulfilling Old Testament prophecy, emphasizing His teaching authority through five major discourses.',
    metadata: {
      testament: 'new',
      order: 40
    }
  },
  {
    id: 'mar',
    title: 'Mark',
    shortName: 'Mark',
    category: 'gospels',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 16,
    compositionDate: '~65-70 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'John Mark',
    introduction: 'Mark is the earliest gospel, presenting Jesus as the suffering servant who comes to serve and give His life as a ransom.',
    metadata: {
      testament: 'new',
      order: 41
    }
  },
  {
    id: 'luk',
    title: 'Luke',
    shortName: 'Luke',
    category: 'gospels',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 24,
    compositionDate: '~80-90 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Luke',
    introduction: 'Luke emphasizes Jesus\' compassion for the marginalized and traces His ministry from birth through resurrection and ascension.',
    metadata: {
      testament: 'new',
      order: 42
    }
  },
  {
    id: 'joh',
    title: 'John',
    shortName: 'John',
    category: 'gospels',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 21,
    compositionDate: '~90-100 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'John the Apostle',
    introduction: 'John presents Jesus as the divine Word made flesh, emphasizing His identity as the Son of God through selected signs and discourses.',
    metadata: {
      testament: 'new',
      order: 43
    }
  },
  {
    id: 'act',
    title: 'Acts',
    shortName: 'Acts',
    category: 'history',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 28,
    compositionDate: '~80-90 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Luke',
    introduction: 'Acts chronicles the early church\'s growth from Jerusalem to Rome, featuring Peter, Paul, and the spread of the gospel.',
    metadata: {
      testament: 'new',
      order: 44
    }
  },
  {
    id: 'rom',
    title: 'Romans',
    shortName: 'Rom',
    category: 'epistles',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 16,
    compositionDate: '~57 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Paul',
    introduction: 'Romans is Paul\'s systematic presentation of the gospel, explaining justification by faith and God\'s plan for Jew and Gentile.',
    metadata: {
      testament: 'new',
      order: 45
    }
  },
  {
    id: '1co',
    title: '1 Corinthians',
    shortName: '1 Cor',
    category: 'epistles',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 16,
    compositionDate: '~54-55 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Paul',
    introduction: '1 Corinthians addresses divisions, immorality, and misuse of spiritual gifts in the Corinthian church.',
    metadata: {
      testament: 'new',
      order: 46
    }
  },
  {
    id: 'gal',
    title: 'Galatians',
    shortName: 'Gal',
    category: 'epistles',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 6,
    compositionDate: '~48-55 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'Paul',
    introduction: 'Galatians defends justification by faith alone against those requiring Gentile converts to follow Jewish law.',
    metadata: {
      testament: 'new',
      order: 48
    }
  },
  {
    id: 'eph',
    title: 'Ephesians',
    shortName: 'Eph',
    category: 'epistles',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 6,
    compositionDate: '~60-62 CE',
    compositionConfidence: 'debated',
    traditionalAuthor: 'Paul',
    introduction: 'Ephesians explores the church as Christ\'s body, emphasizing unity, spiritual blessings, and practical Christian living.',
    metadata: {
      testament: 'new',
      order: 49
    }
  },
  {
    id: 'rev',
    title: 'Revelation',
    shortName: 'Rev',
    category: 'apocalypse',
    canonStatus: {
      protestant: 'canonical',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 22,
    compositionDate: '~90-96 CE',
    compositionConfidence: 'scholarly-consensus',
    traditionalAuthor: 'John the Apostle',
    introduction: 'Revelation presents apocalyptic visions of cosmic conflict, divine judgment, and ultimate restoration through rich symbolic imagery.',
    metadata: {
      testament: 'new',
      order: 66
    }
  },
  {
    id: 'tob',
    title: 'Tobit',
    shortName: 'Tob',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 14,
    compositionDate: '~225-175 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: 'Tobit narrates the story of a righteous Israelite and his son Tobias, emphasizing faithfulness, prayer, and divine providence.',
    metadata: {
      testament: 'other',
      order: 67
    }
  },
  {
    id: 'jdt',
    title: 'Judith',
    shortName: 'Jdt',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 16,
    compositionDate: '~150 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: 'Judith tells of a brave Jewish widow who saves her people from an Assyrian general through courage and cunning.',
    metadata: {
      testament: 'other',
      order: 68
    }
  },
  {
    id: 'wis',
    title: 'Wisdom of Solomon',
    shortName: 'Wis',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 19,
    compositionDate: '~100-50 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: 'Wisdom reflects on righteousness, immortality, and God\'s providence, blending Jewish theology with Greek philosophical concepts.',
    metadata: {
      testament: 'other',
      order: 69
    }
  },
  {
    id: 'sir',
    title: 'Sirach (Ecclesiasticus)',
    shortName: 'Sir',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 51,
    compositionDate: '~180 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: 'Sirach offers practical wisdom for daily living, combining traditional Jewish teachings with ethical instructions.',
    metadata: {
      testament: 'other',
      order: 70
    }
  },
  {
    id: '1ma',
    title: '1 Maccabees',
    shortName: '1 Macc',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 16,
    compositionDate: '~100 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: '1 Maccabees chronicles the Jewish revolt against Seleucid oppression and the rededication of the Temple.',
    metadata: {
      testament: 'other',
      order: 71
    }
  },
  {
    id: '2ma',
    title: '2 Maccabees',
    shortName: '2 Macc',
    category: 'deuterocanon',
    canonStatus: {
      protestant: 'apocryphal',
      catholic: 'canonical',
      orthodox: 'canonical',
      jewish: 'non-canonical',
      ethiopian: 'canonical'
    },
    chaptersCount: 15,
    compositionDate: '~124 BCE',
    compositionConfidence: 'scholarly-consensus',
    introduction: '2 Maccabees provides a theological interpretation of the Maccabean revolt, emphasizing divine intervention and martyrdom.',
    metadata: {
      testament: 'other',
      order: 72
    }
  }
]

export const sampleVerses: VerseUnit[] = [
  {
    id: 'gen-1-1-geneva',
    workId: 'gen',
    chapterNumber: 1,
    verseNumber: 1,
    translationId: 'geneva',
    text: 'In the beginning God created the heaven and the earth.',
    crossReferences: ['joh-1-1', 'heb-11-3']
  },
  {
    id: 'gen-1-1-kjv',
    workId: 'gen',
    chapterNumber: 1,
    verseNumber: 1,
    translationId: 'kjv',
    text: 'In the beginning God created the heaven and the earth.'
  },
  {
    id: 'gen-1-1-esv',
    workId: 'gen',
    chapterNumber: 1,
    verseNumber: 1,
    translationId: 'esv',
    text: 'In the beginning, God created the heavens and the earth.'
  },
  {
    id: 'gen-1-1-niv',
    workId: 'gen',
    chapterNumber: 1,
    verseNumber: 1,
    translationId: 'niv',
    text: 'In the beginning God created the heavens and the earth.'
  },
  {
    id: 'joh-3-16-geneva',
    workId: 'joh',
    chapterNumber: 3,
    verseNumber: 16,
    translationId: 'geneva',
    text: 'For God so loveth the world, that he hath given his only begotten Son, that whosoever believeth in him, should not perish, but have everlasting life.'
  },
  {
    id: 'joh-3-16-kjv',
    workId: 'joh',
    chapterNumber: 3,
    verseNumber: 16,
    translationId: 'kjv',
    text: 'For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.'
  },
  {
    id: 'joh-3-16-esv',
    workId: 'joh',
    chapterNumber: 3,
    verseNumber: 16,
    translationId: 'esv',
    text: 'For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life.'
  },
  {
    id: 'joh-3-16-niv',
    workId: 'joh',
    chapterNumber: 3,
    verseNumber: 16,
    translationId: 'niv',
    text: 'For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.'
  }
]

export const timelineEvents: HistoricalEvent[] = [
  {
    id: 'event-creation-narrative',
    title: 'Creation Narrative Era',
    date: '~4000-2000 BCE (Traditional)',
    dateConfidence: 'traditional',
    era: 'Primordial',
    category: 'narrative',
    description: 'Traditional dating places the creation accounts and early Genesis narratives in this period. Modern scholarship views these as theological narratives compiled much later, drawing on ancient Near Eastern creation traditions.',
    sources: [
      {
        id: 'src-gen-dating',
        title: 'Genesis dating debates',
        notes: 'Traditional vs critical scholarship perspectives'
      }
    ],
    relatedWorks: ['gen'],
    tradition: 'jewish'
  },
  {
    id: 'event-exodus',
    title: 'Exodus from Egypt',
    date: '~1446 BCE or ~1260 BCE',
    dateConfidence: 'debated',
    era: 'Bronze Age',
    category: 'narrative',
    description: 'The biblical account places Israel\'s departure from Egypt and wilderness wandering in this era. Archaeological evidence for the Exodus remains debated, with scholars proposing various dates or viewing it as theological narrative rather than historical event.',
    sources: [
      {
        id: 'src-exodus-dating',
        title: 'Exodus dating debates',
        author: 'Various scholars',
        notes: 'Early date (1446 BCE) vs late date (1260 BCE) theories'
      }
    ],
    relatedWorks: ['exo'],
    tradition: 'jewish'
  },
  {
    id: 'event-torah-composition',
    title: 'Torah Composition and Editing',
    date: '~900-400 BCE',
    dateConfidence: 'scholarly-consensus',
    era: 'Iron Age',
    category: 'composition',
    description: 'Critical scholarship dates the compilation and editing of the Torah (Genesis-Deuteronomy) to this period, drawing on earlier oral and written traditions. The Documentary Hypothesis proposes multiple sources woven together during Israel\'s monarchy and exile.',
    sources: [
      {
        id: 'src-documentary-hypothesis',
        title: 'Documentary Hypothesis',
        author: 'Julius Wellhausen',
        year: 1878
      }
    ],
    relatedWorks: ['gen', 'exo'],
    tradition: 'jewish'
  },
  {
    id: 'event-septuagint',
    title: 'Septuagint Translation',
    date: '~250 BCE',
    dateConfidence: 'scholarly-consensus',
    era: 'Hellenistic Period',
    category: 'canon-formation',
    description: 'Greek-speaking Jews in Alexandria translated Hebrew scriptures into Greek, creating the Septuagint (LXX). This translation became the Old Testament for early Christians and influenced New Testament quotations.',
    sources: [
      {
        id: 'src-septuagint',
        title: 'Letter of Aristeas',
        notes: 'Ancient account of translation origins'
      }
    ],
    relatedWorks: ['gen', 'exo'],
    tradition: 'jewish'
  },
  {
    id: 'event-jamnia',
    title: 'Council of Jamnia (Traditional)',
    date: '~90-100 CE',
    dateConfidence: 'debated',
    era: 'Roman Period',
    category: 'canon-formation',
    description: 'Traditionally cited as when Jewish scholars finalized the Hebrew Bible canon, though modern scholarship questions whether a formal council occurred. The rabbinic discussions at Jamnia did address scriptural debates.',
    sources: [
      {
        id: 'src-jamnia-debate',
        title: 'Jamnia hypothesis debate',
        notes: 'Questioning traditional narrative of canon closure'
      }
    ],
    relatedWorks: [],
    tradition: 'jewish'
  },
  {
    id: 'event-jerome-vulgate',
    title: 'Jerome\'s Vulgate Translation',
    date: '382-405 CE',
    dateConfidence: 'scholarly-consensus',
    era: 'Late Antiquity',
    category: 'community-history',
    description: 'Jerome translated the Bible into Latin from Hebrew and Greek sources, creating the Vulgate that became the Catholic Church\'s standard text for over a millennium.',
    sources: [
      {
        id: 'src-vulgate',
        title: 'Jerome\'s letters and prefaces',
        author: 'Jerome'
      }
    ],
    relatedWorks: [],
    tradition: 'catholic'
  },
  {
    id: 'event-tyndale',
    title: 'Tyndale\'s English Translation',
    date: '1526',
    dateConfidence: 'scholarly-consensus',
    era: 'Reformation',
    category: 'community-history',
    description: 'William Tyndale\'s groundbreaking English translation from Hebrew and Greek laid the foundation for all subsequent English Bibles, including the Geneva and King James versions. Tyndale was executed for heresy in 1536.',
    sources: [
      {
        id: 'src-tyndale',
        title: 'Tyndale biography',
        author: 'David Daniell',
        year: 1994
      }
    ],
    relatedWorks: [],
    tradition: 'protestant'
  },
  {
    id: 'event-geneva-bible',
    title: 'Geneva Bible Published',
    date: '1560',
    dateConfidence: 'scholarly-consensus',
    era: 'Reformation',
    category: 'community-history',
    description: 'English Protestant exiles in Geneva produced this landmark translation with extensive Reformed theological notes. It became the Bible of English Puritans, Scottish Presbyterians, and American colonists, remaining dominant until the KJV gained popularity.',
    sources: [
      {
        id: 'src-geneva',
        title: 'The Geneva Bible: A facsimile',
        year: 1969
      }
    ],
    relatedWorks: [],
    tradition: 'protestant'
  },
  {
    id: 'event-kjv',
    title: 'King James Version Published',
    date: '1611',
    dateConfidence: 'scholarly-consensus',
    era: 'Early Modern',
    category: 'community-history',
    description: 'Commissioned by King James I to create an authoritative English Bible without controversial notes, 47 scholars produced a translation that became the most influential English Bible, shaping language and literature for centuries.',
    sources: [
      {
        id: 'src-kjv',
        title: 'God\'s Secretaries',
        author: 'Adam Nicolson',
        year: 2003
      }
    ],
    relatedWorks: [],
    tradition: 'protestant'
  },
  {
    id: 'event-dead-sea-scrolls',
    title: 'Dead Sea Scrolls Discovery',
    date: '1947-1956',
    dateConfidence: 'scholarly-consensus',
    era: 'Modern',
    category: 'canon-formation',
    description: 'Discovery of ancient Hebrew manuscripts at Qumran provided the oldest known biblical texts, confirming the remarkable accuracy of medieval Hebrew manuscripts while revealing some textual variations.',
    sources: [
      {
        id: 'src-dss',
        title: 'The Dead Sea Scrolls',
        author: 'Geza Vermes',
        year: 1997
      }
    ],
    relatedWorks: [],
    tradition: 'jewish'
  }
]
