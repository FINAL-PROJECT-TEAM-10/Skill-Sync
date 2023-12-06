import unittest
from datetime import datetime

from unittest.mock import Mock, patch

from services import job_ads_services
from app_models.job_ads_models import Job_ad

def fake_job_ad():
    job_ad = Mock()
    job_ad.description = 'description'
    job_ad.location_name = 'city'
    job_ad.remote_status = 0
    job_ad.min_salary = 1000
    job_ad.max_salary = 2000
    job_ad.status = 'status'

    return job_ad

class JobAdsServices_Should(unittest.TestCase):
    # The bottom two tests will be the basis for the object-centred future
    # direction of the project.
    def test_getJobAdAsObject_ReturnsJobAdObject(self):
        job_ad_id = 1
        now = datetime.now()

        with patch('services.job_ads_services.read_query') as read_query:
            read_query.return_value = (
                'description', 'city', 0, 1000, 2000, 'status', now
            )

            result = job_ads_services.get_job_ad_as_object(job_ad_id)

        self.assertIsInstance(result, Job_ad)
        self.assertEqual('description', result.description)
        self.assertEqual('city', result.location_name)
        self.assertEqual(0, result.remote_status)
        self.assertEqual(1000, result.min_salary)
        self.assertEqual(2000, result.max_salary)
        self.assertEqual('status', result.status)
        self.assertEqual(now, result.date_posted)

    def test_getJobAdAsObject_ReturnsNone_IfNotFound(self):
        pass

    def test_findCompany_ReturnsInteger(self):
        pass

    def test_findCompany_ReturnsNone_IfNotFound(self):
        pass

    def test_findNameById_ReturnsStr(self):
        pass

    def test_findNameById_ReturnsNone_IfNotFound(self):
        pass

    def test_createJobAd_ReturnsJobAd(self):
        pass

    def test_createJobAd_UsesInsertQuery(self):
        pass

    def test_createJobAd_RaisesException_IfNoLocationAndNotRemote(self):
        pass

    def test_checkCompanyExists_ReturnsTrue_IfCompany(self):
        pass

    def test_checkCompanyExists_ReturnsFalse_IfNotFound(self):
        pass

    def test_viewAllJobAds_ReturnsList(self):
        pass

    @unittest.skip("Optional test: will be used for future object-centred refactoring")
    def test_viewJobAdsById_ReturnsJobAd(self):
        pass

    def test_currentActiveJobAd_ReturnsNumberOfJobAds(self):
        pass

    # Services method needs to be renamed.
    def test_findJobAdById_ReturnsInteger(self):
        pass

    def test_findJobAdById_ReturnsNone_IfNotFound(self):
        pass

    def test_checkOwnerCompanyReturnsTrue_IfFound(self):
        pass

    def test_checkOwnerCompanyReturnsFalse_IfNotFound(self):
        pass

    @unittest.skip("Testing for this was skipped.\n"
                   "Reason: The logic for this test is identical to the logic\n"
                   "of other similar tests that rely on a single query.\n"
                   "Importantly, we will be moving at a future point to a more\n"
                   "object-centred approach.\n"
                   "Such functions would be deprecated\n\n"
                   "Conclusion: testing for this is a waste of resources.")
    def test_checkCompanyInformation_ReturnsList(self):
        pass


    def test_editJobAds_UsesUpdateQuery(self):
        pass

    def test_editJobAds_RaisesException_IfLevelHigherThanAdvanced(self):
        pass

    @unittest.skip("Currently this returns a JSONResponse.\n"
                   "The logic would be identical for a HTTPException with a status code 200.\n"
                   "Which can be used better by our front-end.")
    def test_editJobAds_RaisesSuccessfulException_WhenCompleted(self):
        pass

    def test_existingRequirements_ReturnsListOfRequirements(self):
        pass

    def test_findRequirementById_ReturnsString(self):
        pass

    def test_findRequirementById_ReturnsNone_WhenNotFound(self):
        pass

    def test_findRequirementsLevel_ReturnsString(self):
        pass

    def test_findRequirementLevel_ReturnsNone_WhenNotFound(self):
        pass

    def test_findRequirementByName_ReturnsString(self):
        pass

    def test_findRequirementByName_ReturnsNone_WhenNotFound(self):
        pass

    def test_checkRequirementAdExist_ReturnsTrue_WhenFound(self):
        pass

    def test_checkRequirementAdExist_ReturnsFalse_WhenNotFound(self):
        pass

    def test_convertLevelName_ReturnsCorrectInts(self):
        pass

    def test_convertLevelName_RaisesException_InvalidInput(self):
        pass

    def test_getLevelJobAd_ReturnsString(self):
        pass

    def test_getLevelJobAd_ReturnsNone_IfNotFound(self):
        pass

    # Method in services needs to be renamed to get_current_job_ads requirements
    def test_getCurrentJobAd_ReturnsCorrectlyFormattedList(self):
        pass

    #HARD TO TEST, needs lots of patching
    def test_calculatePercentageCv_ReturnsCorrectPercentages(self):
        pass

    def test_GetSkillName_ReturnsString(self):
        pass

    def test_GetSkillName_ReturnsNone_IfNotFound(self):
        pass

    def test_getLevel_ReturnsString(self):
        pass

    def test_getLevel_ReturnsNone_IfNotFound(self):
        pass

    def test_mainCvSkills_ReturnsCorrectlyFormattedList(self):
        pass

    def test_filterByCvSalaries_ReturnsListWithDicts(self):
        pass
    @unittest.skip("Currently this returns a JSONResponse.\n"
                   "The logic would be identical for a HTTPException with a status code 200.\n"
                   "Which can be used better by our front-end.")
    def test_filterByCvSalaries_RaisesNotFoundException(self):
        pass

    # This needs to be renamed in services and here
    def test_findNameForJobSeeker_ReturnsInteger(self):
        pass

    def test_findNameForJobSeeker_ReturnsNone_IfNotFound(self):
        pass

    def test_findUsernameJobSeeker_ReturnsString(self):
        pass

    def test_findUsernameJobSeeker_IfNotFound(self):
        pass

    def test_findSeekerNameCVDescriptionFromCV_ReturnsTwoStrings(self):
        pass

    def test_findSeekerNameCVDescriptionFromCV_ReturnsEmptyList_IfNotFound(self):
        pass

    def test_getCvLocationId_ReturnsInteger(self):
        pass

    def test_getCvLocationId_ReturnsNone_IfNotFound(self):
        pass

    def test_getCvLocationDirectlyById_ReturnsString(self):
        pass

    def test_getCvLocationDirectlyById_ReturnsNone_IfNotFound(self):
        pass

