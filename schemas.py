"""
Database Schemas for Clinical Trials Brokerage App

Each Pydantic model represents a collection in MongoDB.
Collection name = lowercase of class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# -------------------- CTU (Clinical Trial Unit / Study Site) --------------------
class CTUTimelines(BaseModel):
    feasibility_to_hrec_days: Optional[int] = Field(None, ge=0)
    hrec_to_siteinit_days: Optional[int] = Field(None, ge=0)
    siteinit_to_fpi_days: Optional[int] = Field(None, ge=0)

class CTU(BaseModel):
    name: str = Field(..., description="CTU / Site name")
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    # Site metrics
    inpatient_confinement: bool = False
    telemetry_24h: bool = False
    outpatient_clinic: bool = True

    # Trial expertise
    trial_expertise: List[str] = Field(default_factory=list, description="e.g., FIH, Late Phase, Oncology, GMO, Gene Therapy, Multi-Site Competitive Enrolment")

    # Tech stack
    tech_stack: List[str] = Field(default_factory=list, description="e.g., E-Source, Paper")

    # Performance
    recruitment_velocity: Optional[float] = Field(None, ge=0, description="Participants per month")
    data_quality_pdpp: Optional[float] = Field(None, ge=0, description="Protocol deviations per participant")

    timelines: Optional[CTUTimelines] = None

# -------------------- Sponsor (Pharma / Device / SaMD) --------------------
class SponsorStudyLength(BaseModel):
    confinement_days: Optional[int] = Field(None, ge=0)
    outpatient_days: Optional[int] = Field(None, ge=0)
    followup_cadence_days: Optional[int] = Field(None, ge=0)

class SponsorAssessmentIntensity(BaseModel):
    pk_sampling: bool = False
    exploratory_endpoints: bool = False

class SponsorStartupTimelines(BaseModel):
    cta_execution_rate: Optional[float] = Field(None, ge=0, le=100, description="% executed within target window")
    feasibility_turnaround_days: Optional[int] = Field(None, ge=0)

class SponsorMonitoring(BaseModel):
    visit_frequency_days: Optional[int] = Field(None, ge=0)
    cra_query_rate: Optional[float] = Field(None, ge=0)
    query_closure_days: Optional[int] = Field(None, ge=0)

class SponsorBudget(BaseModel):
    screen_fail_reimbursement: Optional[float] = Field(None, ge=0)
    per_patient_payment: Optional[float] = Field(None, ge=0)
    startup_fee: Optional[float] = Field(None, ge=0)

class Sponsor(BaseModel):
    name: str = Field(..., description="Sponsor name")
    ecrf_edc_usability: Optional[float] = Field(None, ge=0, le=10, description="0-10 usability score")
    study_length: Optional[SponsorStudyLength] = None
    assessment_intensity: Optional[SponsorAssessmentIntensity] = None
    eligibility_rigidity_pct: Optional[float] = Field(None, ge=0, le=100, description="% likely to exclude standard population")
    startup_timelines: Optional[SponsorStartupTimelines] = None
    monitoring: Optional[SponsorMonitoring] = None
    trial_expertise: List[str] = Field(default_factory=list, description="Medical Monitor Access, CRA Access, Pharmaceutical niche (MAB, Gene Therapy, Onc, Vaccine)")
    budget: Optional[SponsorBudget] = None

# Note: The Flames database viewer will auto-detect these schemas via /schema endpoint
