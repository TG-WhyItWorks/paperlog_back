from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, exists
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.core.search.models import Paper, PaperLike
from app.core.search.schemas import PaperLikeCreate
from datetime import datetime, UTC

ARXIV_CATEGORY_MAPPING = {
    # Computer Science(cs)
    "cs.AI": "Computer Science: Artificial Intelligence",
    "cs.AR": "Computer Science: Hardware Architecture",
    "cs.CC": "Computer Science: Computational Complexity",
    "cs.CE": "Computer Science: Computational Engineering, Finance, and Science",
    "cs.CG": "Computer Science: Computational Geometry",
    "cs.CL": "Computer Science: Computation and Language",
    "cs.CR": "Computer Science: Cryptography and Security",
    "cs.CV": "Computer Science: Computer Vision and Pattern Recognition",
    "cs.CY": "Computer Science: Computers and Society",
    "cs.DB": "Computer Science: Databases",
    "cs.DC": "Computer Science: Distributed, Parallel, Cluster Computing",
    "cs.DL": "Computer Science: Digital Libraries",
    "cs.DM": "Computer Science: Discrete Mathematics",
    "cs.DS": "Computer Science: Data Structures and Algorithms",
    "cs.ET": "Computer Science: Emerging Technologies",
    "cs.FL": "Computer Science: Formal Languages and Automata Theory",
    "cs.GL": "Computer Science: General Literature",
    "cs.GR": "Computer Science: Graphics",
    "cs.GT": "Computer Science: Computer Science and Game Theory",
    "cs.HC": "Computer Science: Human-Computer Interaction",
    "cs.IR": "Computer Science: Information Retrieval",
    "cs.IT": "Computer Science: Information Theory",
    "cs.LG": "Computer Science: Machine Learning",
    "cs.LO": "Computer Science: Logic in Computer Science",
    "cs.MA": "Computer Science: Multiagent Systems",
    "cs.MM": "Computer Science: Multimedia",
    "cs.MS": "Computer Science: Mathematical Software",
    "cs.NA": "Computer Science: Numerical Analysis",
    "cs.NE": "Computer Science: Neural and Evolutionary Computing",
    "cs.NI": "Computer Science: Networking and Internet Architecture",
    "cs.OH": "Computer Science: Other Computer Science",
    "cs.OS": "Computer Science: Operating Systems",
    "cs.PF": "Computer Science: Performance",
    "cs.PL": "Computer Science: Programming Languages",
    "cs.RO": "Computer Science: Robotics",
    "cs.SC": "Computer Science: Symbolic Computation",
    "cs.SD": "Computer Science: Sound",
    "cs.SE": "Computer Science: Software Engineering",
    "cs.SI": "Computer Science: Social and Information Networks",
    "cs.SY": "Computer Science: Systems and Control",
    
    # Economics (econ)
    "econ.EM": "Economics: Econometrics",
    "econ.GN": "Economics: General Economics",
    "econ.TH": "Economics: Theoretical Economics",
    
    # Electrical Engineering and Systems Science (eess)
    "eess.AS": "Electrical Engineering and Systems Science: Audio and Speech Processing",
    "eess.IV": "Electrical Engineering and Systems Science: Image and Video Processing",
    "eess.SP": "Electrical Engineering and Systems Science: Signal Processing",
    "eess.SY": "Electrical Engineering and Systems Science: Systems and Control",
    
    # Mathematics (math)
    "math.AC": "Mathematics: Commutative Algebra",
    "math.AG": "Mathematics: Algebraic Geometry",
    "math.AP": "Mathematics: Analysis of PDEs",
    "math.AT": "Mathematics: Algebraic Topology",
    "math.CA": "Mathematics: Classical Analysis and ODEs",
    "math.Co": "Mathematics: Combinatorics",
    "math.CT": "Mathematics: Category Theory",
    "math.CV": "Mathematics: Complex Variables",
    "math.DG": "Mathematics: Differential Geometry",
    "math.DS": "Mathematics: Dynamical Systems",
    "math.FA": "Mathematics: Functional Analysis",
    "math.GM": "Mathematics: General Mathematics",
    "math.GN": "Mathematics: General Topology", 
    "math.GR": "Mathematics: Group Theory",
    "math.GT": "Mathematics: Geometric Topology",
    "math.HO": "Mathematics: History and Overview",
    "math.IT": "Mathematics: Information Theory",
    "math.KT": "Mathematics: K-Theory and Homology",
    "math.LO": "Mathematics: Logic",
    "math.MG": "Mathematics: Metric Geometry",
    "math.MP": "Mathematics: Mathematical Physics",
    "math.NA": "Mathematics: Numerical Analysis",
    "math.NT": "Mathematics: Number Theory",
    "math.OA": "Mathematics: Operator Algebras",
    "math.OC": "Mathematics: Optimization and Control",
    "math.PR": "Mathematics: Probability",
    "math.QA": "Mathematics: Quantum Algebra",
    "math.RA": "Mathematics: Rings and Algebras",
    "math.RT": "Mathematics: Representation Theory",
    "math.SG": "Mathematics: Symplectic Geometry",
    "math.SP": "Mathematics: Spectral Theory",
    "math.ST": "Mathematics: Statistics Theory",
    
    # Physics (physics)
    "physics.acc-ph": "Physics: Accelerator Physics",
    "physics.ao-ph": "Physics: Atmospheric and Oceanic Physics",
    "physics.app-ph": "Physics: Applied Physics",
    "physics.atm-clus": "Physics: Atomic and Molecular Clusters",
    "physics.atom-ph": "Physics: Atomic Physics",
    "physics.bio-ph": "Physics: Biological Physics",
    "physics.chem-ph": "Physics: Chemical Physics",
    "physics.class-ph": "Physics: Classical Physics",
    "physics.comp-ph": "Physics: Computational Physics",
    "physics.data-an": "Physics: Data Analysis, Statistics and Probability",
    "physics.ed-ph": "Physics: Physics Education",
    "physics.flu-dyn": "Physics: Fluid Dynamics",
    "physics.gen-ph": "Physics: General Physics",
    "physics.geo-ph": "Physics: Geophysics",
    "physics.hist-ph": "Physics: History and Philosophy of Physics",
    "physics.ins-det": "Physics: Instrumentation and Detectors",
    "physics.med-ph": "Physics: Medical Physics",
    "physics.optics": "Physics: Optics",
    "physics.plasm-ph": "Physics: Plasma Physics",
    "physics.pop-ph": "Physics: Popular Physics",
    "physics.soc-ph": "Physics: Physics and Society",
    "physics.space-ph": "Physics: Space Physics",
    
    # Quantum Physics
    "quant-ph": "Quantum Physics",
    
    # Quantum Physics
    "quant-ph": "Quantum Physics",

    # Other categories
    "astro-ph": "Astrophysics",
    "astro-ph.CO": "Astrophysics: Cosmology and Nongalactic Astrophysics",
    "astro-ph.EP": "Astrophysics: Earth and Planetary Astrophysics",
    "astro-ph.GA": "Astrophysics: Astrophysics of Galaxies",
    "astro-ph.HE": "Astrophysics: High Energy Astrophysical Phenomena",
    "astro-ph.IM": "Astrophysics: Instrumentation and Methods for Astrophysics",
    "astro-ph.SR": "Astrophysics: Solar and Stellar Astrophysics",
    "cond-mat": "Condensed Matter",
    "cond-mat.dis-nn": "Condensed Matter: Disordered Systems and Neural Networks",
    "cond-mat.mes-hall": "Condensed Matter: Mesoscale and Nanoscale Physics",
    "cond-mat.mtrl-sci": "Condensed Matter: Materials Science",
    "cond-mat.other": "Condensed Matter: Other Condensed Matter",
    "cond-mat.quant-gas": "Condensed Matter: Quantum Gases",
    "cond-mat.soft": "Condensed Matter: Soft Condensed Matter", "cond-mat.stat-mech": "Condensed Matter: Statistical Mechanics", "cond-mat.str-el": "Condensed Matter: Strongly Correlated Electrons", "cond-mat.supr-con": "Condensed Matter: Superconductivity",
    "gr-qc": "General Relativity and Quantum Cosmology",
    "hep-ex": "High Energy Physics: Experiment",
    "hep-lat": "High Energy Physics: Lattice",
    "hep-ph": "High Energy Physics: Phenomenology",
    "hep-th": "High Energy Physics: Theory",
    "math-ph": "Mathematical Physics",
    "nlin": "Nonlinear Sciences",
    "nlin.AO": "Nonlinear Sciences: Adaptation and Self-Organizing Systems", "nlin.CG": "Nonlinear Sciences: Cellular Automata and Lattice Gases",
    "nlin.CD": "Nonlinear Sciences: Chaotic Dynamics",
    "nlin.PS": "Nonlinear Sciences: Pattern Formation and Solitons",
    "nlin.SI": "Nonlinear Sciences: Exactly Solvable and Integrable Systems",
    "nucl-ex": "Nuclear Experiment",
    "nucl-th": "Nuclear Theory",
    "q-bio": "Quantitative Biology",
    "q-bio.BM": "Quantitative Biology: Biomolecules",
    "q-bio.CB": "Quantitative Biology: Cell Behavior",
    "q-bio.GN": "Quantitative Biology: Genomics",
    "q-bio.MN": "Quantitative Biology: Molecular Networks",
    "q-bio.NC": "Quantitative Biology: Neurons and Cognition",
    "q-bio.OT": "Quantitative Biology: Other Quantitative Biology",
    "q-bio.PE": "Quantitative Biology: Populations and Evolution",
    "q-bio.QM": "Quantitative Biology: Quantitative Methods",
    "q-bio.SC": "Quantitative Biology: Subcellular Processes",
    "q-bio.TO":"Quantitative Biology: Tissues and Organs",
    "q-fin": "Quantitative Finance",
    "q-fin.CP": "Quantitative Finance: Computational Finance",
    "q-fin.EC": "Quantitative Finance: Economics",
    "q-fin.GN": "Quantitative Finance: General Finance",
    "q-fin.MF": "Quantitative Finance: Mathematical Finance",
    "q-fin.PM": "Quantitative Finance: Portfolio Management",
    "q-fin.PR": "Quantitative Finance: Pricing of Securities",
    "q-fin.RM": "Quantitative Finance: Risk Management",
    "q-fin.ST": "Quantitative Finance: Statistical Finance",
    "q-fin.TR": "Quantitative Finance: Trading and Market Microstructure",
    "stat": "Statistics",
    "stat.AP": "Statistics: Applications",
    "stat.CO": "Statistics: Computation",
    "stat.ME": "Statistics: Methodology",
    "stat.ML": "Statistics: Machine Learning",
    "stat.OT": "Statistics: Other Statistics",
    "stat.TH": "Statistics: Statistics Theory",
}


def convert_arxiv_categories(categories) -> str:
    """ 카테고리 이름 변경하고 ; 구분자로 구분"""
    if not categories:
        return ""
    
    category_list = [cat.strip() for cat in categories if cat.strip()]
    
    category_groups = {}
    unmapped_categories = []
    
    for category in category_list:
        category = category.strip()
        
        if category in ARXIV_CATEGORY_MAPPING:
            full_name = ARXIV_CATEGORY_MAPPING[category]
            
            parts = full_name.split(': ', 1)
            main_category = parts[0]
            sub_category = parts[1] if len(parts) > 1 else ""
            
            # ':' 로 구분하여 큰 범위와 작은 범위 분리
            if main_category not in category_groups:
                category_groups[main_category] = set()
            if sub_category:
                sub_category = sub_category.replace(', ', ' & ')
                category_groups[main_category].add(sub_category)
            else:
                # sub_category가 없는 경우 빈 set으로 유지(큰 범위만 표시)
                pass
        else:
            pass # 매핑에 없는 카테고리는 올리지 않음
            """
            # 매핑에 없는 카테고리 처리
            unmapped_categories.append(category)
            #print(f"'{category}' not found in mapping")
            
            # 매핑에 없는 카테고리는 "Other"로 분류
            if "Other" not in category_groups:
                category_groups["Other"] = set()
                category_groups["Other"].add(category)
            """
                
    result_parts = []
    for main_category in sorted(category_groups.keys()):
        sub_categories = sorted(list(category_groups[main_category]))  
        if sub_categories:
            sub_category_str = ";".join(sub_categories)
            result_parts.append(f"{main_category}: {sub_category_str}")
        else:
            # 작은 범위가 없는 경우 큰 범위만 표시
            result_parts.append(f"{main_category}")
            
    return " | ".join(result_parts)




    
    
def list_to_str(lst):
    if isinstance(lst, list):
        return ",".join(lst)
    return lst

async def get_paper_by_arxiv_id(db:AsyncSession, arxiv_id: str):
    stmt = select(Paper).filter(Paper.arxiv_id == arxiv_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    
    
async def save_paper(db: AsyncSession, paper_data: dict):
    # list->str (db엔 list 저장 안되기 때문)
    paper_data["authors"] = list_to_str(paper_data.get("authors", ""))
    paper_data["categories"] = list_to_str(paper_data.get("categories", ""))
    
    paper = Paper(**paper_data)
    db.add(paper)
        
async def update_paper(db: AsyncSession, db_paper: Paper, paper_data: dict):
    
    if "authors" in paper_data:
        paper_data["authors"] = list_to_str(paper_data["authors"])
    if "categories" in paper_data:
        paper_data["categories"] = list_to_str(paper_data["categories"])
    
    # paper_data 내 필드를 db_paper에 업데이트
    for key, value in paper_data.items():
        setattr(db_paper, key, value)
    db_paper.updated_at = datetime.now(UTC)
        
        
async def save_new_papers(db: AsyncSession, papers: list[dict]):
    for data in papers:
        existing_paper = await get_paper_by_arxiv_id(db, data["arxiv_id"])
        
        if "categories" in data:
            print(data["categories"])
            data["categories"] = convert_arxiv_categories(data["categories"])
        
        if not existing_paper:
            await save_paper(db, data)
        else:
            # publish_updated가 다르면 업데이트 처리
            if existing_paper.publish_updated != data["publish_updated"]:
                update_data = data.copy()
                update_data["publish_updated"] = update_data.pop("publish_updated")
                await update_paper(db, existing_paper, update_data)
    await db.commit()
    
    
    
async def get_paginated_papers(db:AsyncSession, page: int, page_size: int = 10):
    stmt = select(Paper).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_paginated_papers_with_like_info(
    db: AsyncSession,
    arxiv_ids:List[str],
    user_id: Optional[int] = None
):
    
    if not arxiv_ids:
        return []
    
    like_count_subq = (
        select(func.count(PaperLike.id))
        .where(PaperLike.paper_id == Paper.id)
        .scalar_subquery()
        .label("like_count")
    )
    
    
    
    if user_id:
        is_liked_subq = (
            select(func.count(PaperLike.id))
            .where(
                and_(
                    PaperLike.paper_id == Paper.id,
                    PaperLike.user_id == user_id
                )
            )
            .scalar_subquery() > 0
        ).label("is_liked")
        
        stmt = (
            select(Paper, like_count_subq, is_liked_subq)
            .where(Paper.arxiv_id.in_(arxiv_ids))
        )
    else:
        stmt = (
            select(Paper, like_count_subq)
            .where(Paper.arxiv_id.in_(arxiv_ids))
        )
        
    result = await db.execute(stmt)
    
    # arxiv 순서 유지를 위한 딕셔너리 생성
    papers_dict = {}
    for row in result:
        paper = row[0]
        papers_dict[paper.arxiv_id] = row
    
    # arxiv 순서대로 정렬된 결과 생성
    papers_data = []
    for arxiv_id in arxiv_ids:
        if arxiv_id in papers_dict:
            row = papers_dict[arxiv_id]
            paper = row[0]
            like_count = row[1]
        
        
            paper_dict = {
                "id": paper.id,
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors,
                "summary": paper.summary,
                "link": paper.link,
                "published": paper.published,
                "publish_updated": paper.publish_updated,
                "categories": paper.categories,
                "doi": paper.doi,
                "created_at": paper.created_at,
                "updated_at": paper.updated_at,
                "reviews": paper.reviews,
                "like_count": like_count
            }
        
            if user_id:
                is_liked = row[2] # 사용자 좋아요 여부
                paper_dict["is_liked"] = is_liked
            
            papers_data.append(paper_dict)
        
    return papers_data

async def get_papers_with_like_info(db: AsyncSession, arxiv_id: str, user_id: Optional[int] = None):
    """좋아요 정보를 포함한 특정 논문 조회"""
    
    like_count_subq = (
        select(func.count(PaperLike.id))
        .where(PaperLike.paper_id == Paper.id)
        .scalar_subquery()
        .label("like_count")
    )
    # 로그인 했을 때만 유저가 좋아요 했는지 체크
    if user_id:
        is_liked_subq = (
            select(func.count(PaperLike.id))
            .where(
                and_(
                    PaperLike.paper_id == Paper.id,
                    PaperLike.user_id == user_id
                )
            )
            .scalar_subquery() > 0
        ).label("is_liked")
        
        stmt = (
            select(Paper, like_count_subq, is_liked_subq)
            .filter(Paper.arxiv_id == arxiv_id)
        )
    else:
        stmt = (
            select(Paper, like_count_subq)
            .filter(Paper.arxiv_id == arxiv_id)
        )
        
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        return None
    
    paper = row[0] # Paper 객체
    like_count = row[1] # 좋아요 수
    
    paper_dict = {
            #"id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "summary": paper.summary,
            "link": paper.link,
            "published": paper.published,
            "publish_updated": paper.publish_updated,
            "categories": paper.categories,
            "doi": paper.doi if paper.doi!=None else 'str',
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "reviews": paper.reviews,
            "like_count": like_count
        }
    
    if user_id:
            is_liked = row[2] # 사용자 좋아요 여부
            paper_dict["is_liked"] = is_liked
            
    return paper_dict



class PaperLikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_like(self, user_id: int, paper_like: PaperLikeCreate) -> PaperLike:
        db_like = PaperLike(
            user_id=user_id,
            paper_id=paper_like.paper_id
            )
        self.db.add(db_like)
        await self.db.commit()
        await self.db.refresh(db_like)
        return db_like
    
    
    async def remove_like(self, user_id: int, paper_id: int) -> bool:
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        like = result.scalar_one_or_none()
        
        if like:
            await self.db.delete(like)
            await self.db.commit()
            return True
        return False
    
    async def get_like(self, user_id: int, paper_id: int) -> Optional[PaperLike]:
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def is_liked_by_user(self, user_id: int, paper_id: int) -> bool:
        """사용자가 특정 논문 좋아요 했는지 확인"""
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar()
    
    
    async def get_like_count(self, paper_id: int) -> int:
        stmt = select(func.count(PaperLike.id)).filter(
            PaperLike.paper_id == paper_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_liked_papers(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Paper]:
        """사용자가 좋아요 누른 논문 목록 조회(좋아요 누른 시각 내림차순)"""
        stmt = (
            select(Paper)
            .join(PaperLike)
            .filter(PaperLike.user_id == user_id)
            .options(selectinload(Paper.paper_likes))
            .order_by(PaperLike.liked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
