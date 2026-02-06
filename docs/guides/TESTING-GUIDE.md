# Testing Guide - BWC Dashboard Improvements

## Quick Test Instructions

### 1. Start the Server

```powershell
# Navigate to project directory
cd C:\web-dev\github-repos\Evident.info

# Start Flask server
python app.py
```

Server should start at: http://localhost:5000

### 2. Access the Dashboard

Navigate to: http://localhost:5000/bwc-dashboard.html

### 3. Test Checklist

#### Visual Elements ✓

- [ ] Stats overview cards display at top
- [ ] Filter dropdown shows status options
- [ ] Sort dropdown shows sorting options
- [ ] ➕ New Analysis button visible in header
- [ ] Analysis cards render in grid layout
- [ ] Empty state shows if no analyses

#### Filtering & Sorting ✓

- [ ] Click status filter - cards update instantly
- [ ] Try each status: All, Uploaded, Analyzing, Completed, Failed
- [ ] Click sort dropdown - cards reorder
- [ ] Try: Most Recent, Oldest First, Name A-Z

#### Timeline Visualization ✓

- [ ] Timeline bar appears on completed analyses
- [ ] Color-coded segments visible
- [ ] Duration displays properly (M:SS format)
- [ ] Hover over segments shows interaction

#### Quick Insights ✓

- [ ] Insights panel shows below timeline
- [ ] Duration insight displays correctly
- [ ] Speaker count insight shows
- [ ] Segment count insight displays
- [ ] Critical alerts appear (if critical issues exist)

#### Detail Modal ✓

- [ ] Click "👁️ View Full Analysis" button
- [ ] Modal opens centered on screen
- [ ] Case Information section displays
- [ ] Analysis Results section shows metrics
- [ ] Chain of Custody section visible
- [ ] Export Options show all 5 formats
- [ ] Click X to close modal
- [ ] Click outside modal to close

#### Export Functionality ✓

Test each export format:

- [ ] Click PDF button - download starts
- [ ] Click DOCX button - download starts
- [ ] Click JSON button - download starts
- [ ] Click TXT button - download starts
- [ ] Click MD button - download starts

Verify downloads:

- [ ] PDF opens in PDF reader
- [ ] DOCX opens in Word
- [ ] JSON is valid JSON format
- [ ] TXT is readable text
- [ ] MD renders properly in viewer

#### Real-Time Updates ✓

If you have an analyzing video:

- [ ] Progress bar updates automatically
- [ ] Percentage increases
- [ ] Current step updates
- [ ] Stats overview refreshes
- [ ] Click "🔄 Refresh Status" works

#### Responsive Design ✓

- [ ] Resize browser to tablet width - layout adapts
- [ ] Resize to mobile width - single column
- [ ] Filter/sort dropdowns remain usable
- [ ] Modal scrolls properly on small screens
- [ ] Touch interactions work (if testing on mobile)

#### Icon Buttons ✓

- [ ] Icon-only export buttons render
- [ ] Hover shows tooltip (browser default)
- [ ] Icons have proper spacing
- [ ] Buttons are touch-friendly (44x44px minimum)

### 4. Browser Testing

Test in multiple browsers:

- [ ] Chrome - All features work
- [ ] Firefox - All features work
- [ ] Edge - All features work
- [ ] Safari - All features work (if on Mac)

### 5. Error Handling

Test error scenarios:

- [ ] Try exporting without required dependencies (should show error)
- [ ] Try deleting analysis (should confirm first)
- [ ] Try accessing non-existent analysis (should error gracefully)

### 6. Performance Testing

- [ ] Dashboard loads in <2 seconds
- [ ] Filtering is instant (<100ms)
- [ ] Sorting is instant (<100ms)
- [ ] Modal opens quickly (<500ms)
- [ ] Export completes in <5 seconds

--

## Common Issues & Solutions

### Issue: Dashboard doesn't load

**Solution:** Check if Flask server is running and accessible at http://localhost:5000

### Issue: No analyses show up

**Solution:**

1. Upload a BWC video first
2. Check if logged in as correct user
3. Check browser console for errors

### Issue: Export fails

**Solution:**

```powershell
# Install required dependencies
pip install reportlab python-docx
```

### Issue: Modal doesn't close

**Solution:**

- Click the X button in top-right
- Click outside the modal area
- Refresh the page

### Issue: Real-time updates not working

**Solution:**

1. Check browser console for errors
2. Ensure analysis is actually in "analyzing" state
3. Check network tab for API calls

### Issue: Timeline doesn't show

**Solution:**

- Timeline only shows for completed analyses
- Check if analysis has duration data
- Check if total_speakers > 0

--

## Expected Behavior

### For New User (No Analyses)

1. Stats show all zeros
2. Empty state displays with friendly message
3. "Upload Video" button prominently shown
4. Filter/sort controls still visible but inactive

### For User with Analyses

1. Stats cards show correct counts
2. Grid displays analysis cards
3. Filtering updates cards instantly
4. Sorting reorders cards
5. Real-time updates for analyzing videos

### For Analyzing Video

1. Progress bar animates
2. Status badge pulses
3. Current step updates
4. Stats refresh every 2 seconds
5. "Refresh Status" button available

### For Completed Analysis

1. Full results grid displays
2. Timeline bar shows
3. Quick insights appear
4. All export buttons enabled
5. "View Full Analysis" button works

--

## Sample Test Data

If you need test data, create a sample analysis:

1. Go to /analyzer
2. Upload a video file (MP4, AVI, etc.)
3. Fill in case information:
   - Case Number: TEST-2026-001
   - Evidence Number: EV-001
   - Acquired By: Officer John Smith
   - Source: Dashboard Patrol Unit 5
4. Click "Start Analysis"
5. Return to dashboard to see it appear

--

## Success Criteria

All features pass if:
✅ Dashboard loads without errors
✅ All visual elements render correctly
✅ Filtering and sorting work instantly
✅ Timeline visualizes properly
✅ Insights generate accurately
✅ Modal opens/closes smoothly
✅ All 5 export formats download successfully
✅ Real-time updates function
✅ Responsive design adapts to screen sizes
✅ No JavaScript errors in console
✅ Performance meets targets (<2s load, instant filters)

--

## Reporting Issues

If you encounter bugs:

1. Note the exact steps to reproduce
2. Check browser console for errors (F12)
3. Check network tab for failed requests
4. Note which browser and version
5. Take screenshots if visual issue

--

_Last Updated: January 23, 2026_
