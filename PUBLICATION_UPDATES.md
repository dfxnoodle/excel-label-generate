# Publication Code Updates Summary

## Overview
Updated the publication filtering system to remove deprecated codes and simplify naming.

## Date of Changes
October 10, 2025

## Changes Made

### 1. Removed Deprecated Publication Codes

#### BEC (Bulletin English & Chinese) ❌
- **Status**: Removed completely
- **Reason**: Deprecated - no longer in use
- **Replacement**: Users should select both BE and BC for bilingual recipients
- **Documentation**: See `BEC_DEPRECATION.md`

#### ARE (Annual Report English) ❌
- **Status**: Removed from documentation
- **Reason**: Deprecated - superseded by AR
- **Replacement**: Use AR instead

#### ARC (Annual Report Chinese) ❌
- **Status**: Removed from documentation
- **Reason**: Deprecated - superseded by AR
- **Replacement**: Use AR instead

### 2. Added New Selectable Publication

#### AR (Annual Report) ✅
- **Status**: Now selectable in frontend
- **Location**: Publication filter checkboxes
- **Backend**: Already configured in `publication_options_map`
- **Display Name**: Simplified from "Annual Report (English Only)" to "Annual Report"

## Current Active Publication Codes

### Selectable in Frontend UI:
1. **BE** - Bulletin (English Only)
2. **BC** - Bulletin (Chinese Only)
3. **AR** - Annual Report ⭐ NEW

### Available in Backend (not yet in UI):
4. **FFE** - Facts and Figures (English Only)
5. **FFC** - Facts and Figures (Chinese Only)

## Frontend Changes

### templates/index.html

#### 1. Added AR Checkbox
```html
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="pubAR" value="AR">
    <label class="form-check-label" for="pubAR">
        <strong>AR</strong> - Annual Report
    </label>
</div>
```

#### 2. Updated Publication Info Modal Table
Added AR entry:
```html
<tr>
    <td><code class="fs-6">AR</code></td>
    <td><strong>Annual Report</strong></td>
    <td>University annual report publication</td>
</tr>
```

#### 3. Updated Example Use Cases
Added new examples:
- Annual Report only: Check `AR`
- Bulletin and Annual Report: Check `BE`, `BC`, and `AR`

#### 4. Removed Deprecated References
- Removed ARE and ARC from "Additional Publication Columns" section
- Added FFE and FFC as examples instead

## Backend Changes

### src/simple_labels.py

#### Simplified Naming
```python
# Before:
"Annual Report (English Only)": {"data_columns": ["AR"], "label_codes": ["AR"]}

# After:
"Annual Report": {"data_columns": ["AR"], "label_codes": ["AR"]}
```

**Reason**: Since ARE and ARC are deprecated and only AR exists, no need to specify language.

## Migration Guide

### For Users

**Previously:**
- ARE column → English annual report
- ARC column → Chinese annual report
- BEC column → Both bulletins

**Now:**
- **AR column** → Annual report (language-neutral)
- Select **BE + BC** → Both bulletins

### For Data Files

#### If your Excel has deprecated columns:
- **ARE/ARC columns**: Can remain in file, will be ignored
- **BEC column**: Can remain in file, will be ignored
- **AR column**: Will be recognized and can be filtered

#### Recommended cleanup:
```
Old columns: ARE, ARC, BEC
Keep: AR, BE, BC
Optional: Remove old columns from future data files
```

## Testing

### Frontend Verification ✅
1. Open web interface
2. Navigate to publication filter section
3. Verify three checkboxes: BE, BC, AR
4. Check publication info modal shows BE, BC, AR
5. Verify examples include AR

### Backend Verification ✅
```bash
python -c "import sys; sys.path.insert(0, 'src'); \
from simple_labels import load_config; \
config = load_config(); \
print(list(config['publication_options_map'].keys()))"

# Output should include:
# - Annual Report (not "Annual Report (English Only)")
# - Bulletin (English Only)
# - Bulletin (Chinese Only)
# - Facts and Figures (English Only)
# - Facts and Figures (Chinese Only)
```

### Test Cases

#### Test 1: AR Filter
```javascript
Filter: publication_columns = ["AR"]
Expected: Only recipients with AR >= 1
```

#### Test 2: Multiple Publications
```javascript
Filter: publication_columns = ["BE", "BC", "AR"]
Expected: Recipients with BE >= 1 OR BC >= 1 OR AR >= 1
```

#### Test 3: Backward Compatibility
```
Excel file with: ARE, ARC, BEC, BE, BC, AR columns
System should: Ignore ARE/ARC/BEC, use BE/BC/AR
```

## Files Modified

### Source Code
1. `/templates/index.html`
   - Added AR checkbox
   - Added AR to modal table
   - Updated examples
   - Removed ARE/ARC references

2. `/src/simple_labels.py`
   - Simplified: "Annual Report (English Only)" → "Annual Report"

### Documentation
1. `/SESSION_SUMMARY.md`
   - Updated publication column references
   - Removed ARE/ARC

2. `/BEC_DEPRECATION.md`
   - Documented BEC removal

3. `/PUBLICATION_UPDATES.md`
   - This comprehensive guide (new)

## Summary of Publication System

### Evolution Timeline
```
Phase 1 (Old):
  Bulletins: BE, BC, BEC
  Annual Reports: ARE, ARC

Phase 2 (Current):
  Bulletins: BE, BC
  Annual Report: AR
  
Deprecated: BEC, ARE, ARC
```

### Current State
```
✅ Selectable in UI:
   - BE (Bulletin English)
   - BC (Bulletin Chinese)
   - AR (Annual Report)

✅ Available but not in UI:
   - FFE (Facts & Figures English)
   - FFC (Facts & Figures Chinese)

❌ Deprecated/Removed:
   - BEC (Bulletin English & Chinese)
   - ARE (Annual Report English)
   - ARC (Annual Report Chinese)
```

## Future Enhancements

Consider adding to frontend UI:
- [ ] FFE (Facts and Figures English)
- [ ] FFC (Facts and Figures Chinese)
- [ ] Other custom publication columns as needed

## Support

### Common Questions

**Q: Can I still use my old Excel file with ARE/ARC columns?**
A: Yes! Old columns are simply ignored. The system only looks at AR now.

**Q: What if I check AR but my file has ARE instead?**
A: The system will look for the AR column. If it doesn't exist, no recipients will match this filter.

**Q: Should I rename ARE/ARC columns to AR in my Excel?**
A: Recommended for clarity, but not required. You can keep both or just use AR going forward.

**Q: What happened to bilingual bulletin (BEC)?**
A: Select both BE and BC checkboxes to include recipients subscribed to either or both bulletins.

---

**Status**: ✅ Completed  
**Impact**: Low - Backward compatible  
**Breaking Changes**: None  
**User Action Required**: None (optional: update Excel files)
