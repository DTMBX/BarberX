/**
 * Legal Pages Quality Assurance Test
 * Tests footer links, legal page accessibility, and content integrity
 */

const pages = [
  { url: 'http://localhost:4000/', name: 'Homepage' },
  { url: 'http://localhost:4000/services/', name: 'Services' },
  { url: 'http://localhost:4000/about/', name: 'About' },
  { url: 'http://localhost:4000/contact/', name: 'Contact' },
  { url: 'http://localhost:4000/privacy/', name: 'Privacy' },
  { url: 'http://localhost:4000/terms/', name: 'Terms' },
  { url: 'http://localhost:4000/copyright/', name: 'Copyright' },
  { url: 'http://localhost:4000/disclaimers/', name: 'Disclaimers' }
];

const legalLinks = [
  { text: 'Privacy', href: '/privacy/' },
  { text: 'Terms', href: '/terms/' },
  { text: 'Disclaimers', href: '/disclaimers/' },
  { text: 'Copyright', href: '/copyright/' }
];

async function testPage(page) {
  try {
    const response = await fetch(page.url);
    if (!response.ok) {
      return { ...page, status: 'FAIL', error: `HTTP ${response.status}` };
    }
    
    const html = await response.text();
    
    // Check for footer legal links
    const missingLinks = legalLinks.filter(link => !html.includes(link.href));
    
    // Check for trademark notice
    const hasTrademarkNotice = html.includes('Tillerstead™ and TillerPro™');
    
    // Check for "All Rights Reserved"
    const hasAllRightsReserved = html.includes('All Rights Reserved');
    
    // Check for NJ HIC number
    const hasHICNumber = html.includes('NJ HIC') || html.includes('13VH10808800');
    
    return {
      ...page,
      status: 'PASS',
      missingLinks: missingLinks.length > 0 ? missingLinks.map(l => l.text) : null,
      hasTrademarkNotice,
      hasAllRightsReserved,
      hasHICNumber,
      size: (html.length / 1024).toFixed(2) + ' KB'
    };
  } catch (error) {
    return { ...page, status: 'FAIL', error: error.message };
  }
}

async function testLegalPageContent(url, expectedContent) {
  try {
    const response = await fetch(url);
    const html = await response.text();
    
    const checks = {};
    for (const [key, value] of Object.entries(expectedContent)) {
      checks[key] = html.includes(value);
    }
    
    return { url, status: 'PASS', checks };
  } catch (error) {
    return { url, status: 'FAIL', error: error.message };
  }
}

async function runTests() {
  console.log('🧪 Legal Pages Quality Assurance Test\n');
  console.log('Testing Jekyll server at http://localhost:4000\n');
  
  // Test 1: Footer links on all pages
  console.log('Test 1: Footer Links on All Pages');
  console.log('─'.repeat(80));
  
  const results = [];
  for (const page of pages) {
    const result = await testPage(page);
    results.push(result);
    
    const statusIcon = result.status === 'PASS' ? '✅' : '❌';
    console.log(`${statusIcon} ${result.name.padEnd(20)} ${result.status.padEnd(6)} ${result.size || ''}`);
    
    if (result.missingLinks && result.missingLinks.length > 0) {
      console.log(`   ⚠️  Missing links: ${result.missingLinks.join(', ')}`);
    }
    if (result.hasTrademarkNotice === false) {
      console.log('   ⚠️  Missing trademark notice');
    }
    if (result.hasAllRightsReserved === false) {
      console.log('   ⚠️  Missing "All Rights Reserved"');
    }
    if (result.hasHICNumber === false) {
      console.log('   ⚠️  Missing NJ HIC number');
    }
  }
  
  console.log('\n');
  
  // Test 2: Legal page specific content
  console.log('Test 2: Legal Page Content Verification');
  console.log('─'.repeat(80));
  
  const copyrightChecks = await testLegalPageContent('http://localhost:4000/copyright/', {
    'Copyright Notice': 'Copyright © 2025-2026 Tillerstead LLC',
    'TillerPro™': 'TillerPro™',
    'Trademark Notice': 'Trademark Notice',
    'DMCA': 'DMCA',
    'Reverse Engineering': 'reverse engineer'
  });
  
  console.log('Copyright Page:');
  for (const [check, passed] of Object.entries(copyrightChecks.checks)) {
    console.log(`  ${passed ? '✅' : '❌'} ${check}`);
  }
  
  const disclaimersChecks = await testLegalPageContent('http://localhost:4000/disclaimers/', {
    'NJ HIC License': 'NJ HIC #13VH10808800',
    'Warranty': 'warranty',
    'Limitation of Liability': 'Limitation of Liability',
    'Insurance': 'insurance',
    'TillerPro Disclaimer': 'TillerPro™'
  });
  
  console.log('\nDisclaimers Page:');
  for (const [check, passed] of Object.entries(disclaimersChecks.checks)) {
    console.log(`  ${passed ? '✅' : '❌'} ${check}`);
  }
  
  // Summary
  console.log('\n');
  console.log('Summary');
  console.log('─'.repeat(80));
  
  const totalPages = results.length;
  const passedPages = results.filter(r => r.status === 'PASS').length;
  const failedPages = results.filter(r => r.status === 'FAIL').length;
  
  console.log(`Total Pages Tested: ${totalPages}`);
  console.log(`✅ Passed: ${passedPages}`);
  console.log(`❌ Failed: ${failedPages}`);
  
  const pagesWithAllChecks = results.filter(r => 
    r.hasTrademarkNotice && r.hasAllRightsReserved && r.hasHICNumber && 
    (!r.missingLinks || r.missingLinks.length === 0)
  ).length;
  
  console.log(`\n✨ Pages with complete footer: ${pagesWithAllChecks}/${totalPages}`);
  
  if (passedPages === totalPages && pagesWithAllChecks === totalPages) {
    console.log('\n🎉 ALL TESTS PASSED! Legal protection framework is complete.');
  } else {
    console.log('\n⚠️  Some tests failed. Review output above.');
  }
}

// Run tests
runTests().catch(console.error);
