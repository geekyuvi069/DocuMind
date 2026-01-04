"""
Resume extraction schema and utilities.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ResumeSchema(BaseModel):
    """Schema for resume field extraction."""
    
    name: Optional[str] = Field(None, description="Candidate name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    skills: Optional[List[str]] = Field(None, description="List of skills")
    experience_years: Optional[float] = Field(None, description="Years of experience")
    education: Optional[str] = Field(None, description="Education level")
    current_role: Optional[str] = Field(None, description="Current job title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-234-567-8900",
                "skills": ["Python", "FastAPI", "MongoDB"],
                "experience_years": 5.5,
                "education": "Bachelor's in Computer Science",
                "current_role": "Senior Software Engineer"
            }
        }


def extract_resume_fields(text: str) -> dict:
    """
    Extract resume fields from text using rule-based patterns.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Dictionary with extracted resume fields
    """
    text_lower = text.lower()
    lines = text.split('\n')
    
    extracted = {}
    
    # Extract name (usually first line or after "name:")
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line.split()) <= 4:
            extracted['name'] = first_line
    
    # Extract email
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        extracted['email'] = email_match.group(0)
    
    # Extract phone
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\d{10}',  # 10 digits
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            extracted['phone'] = phone_match.group(0)
            break
    
    # Extract skills (common tech skills)
    common_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'node.js',
        'fastapi', 'django', 'flask', 'mongodb', 'postgresql', 'mysql',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'linux',
        'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'graphql', 'rest api'
    ]
    
    found_skills = []
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    # Also look for skills section
    skills_section = False
    for i, line in enumerate(lines):
        if 'skills' in line.lower() and len(line.split()) <= 3:
            skills_section = True
            # Extract next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                line_lower = lines[j].lower()
                for skill in common_skills:
                    if skill in line_lower and skill.title() not in found_skills:
                        found_skills.append(skill.title())
            break
    
    if found_skills:
        extracted['skills'] = found_skills
    
    # Extract experience years
    experience_keywords = ['experience', 'years', 'yrs', 'yr']
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in experience_keywords):
            # Look for numbers followed by year/yrs
            year_pattern = r'(\d+\.?\d*)\s*(years?|yrs?\.?)'
            year_match = re.search(year_pattern, line_lower)
            if year_match:
                try:
                    years = float(year_match.group(1))
                    extracted['experience_years'] = years
                    break
                except ValueError:
                    pass
    
    # Extract education
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'education']
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in education_keywords):
            if 'bachelor' in line_lower:
                extracted['education'] = "Bachelor's Degree"
            elif 'master' in line_lower:
                extracted['education'] = "Master's Degree"
            elif 'phd' in line_lower or 'ph.d' in line_lower:
                extracted['education'] = "PhD"
            break
    
    # Extract current role (look for job titles)
    role_keywords = ['engineer', 'developer', 'manager', 'analyst', 'architect', 'lead']
    for line in lines[:30]:  # Check first 30 lines
        line_lower = line.lower()
        if any(kw in line_lower for kw in role_keywords):
            # Extract role title
            words = line.split()
            if len(words) <= 5:  # Reasonable title length
                extracted['current_role'] = line.strip()
                break
    
    return extracted

