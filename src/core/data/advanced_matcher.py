"""
Advanced matching system using multiple algorithms and libraries for improved JSON matching.
Combines fuzzy string matching, semantic similarity, and performance optimizations.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from functools import lru_cache
import time

# Import all available matching libraries
try:
    from rapidfuzz import fuzz as rapidfuzz_fuzz, process as rapidfuzz_process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logging.warning("RapidFuzz not available, falling back to FuzzyWuzzy")

try:
    from fuzzywuzzy import fuzz as fuzzywuzzy_fuzz, process as fuzzywuzzy_process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    logging.warning("FuzzyWuzzy not available")

try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False
    logging.warning("Jellyfish not available")

try:
    import difflib
    DIFFLIB_AVAILABLE = True
except ImportError:
    DIFFLIB_AVAILABLE = False
    logging.warning("difflib not available")

@dataclass
class MatchResult:
    """Represents a matching result with detailed scoring information."""
    item: Dict
    overall_score: float
    exact_match: bool = False
    fuzzy_score: float = 0.0
    semantic_score: float = 0.0
    phonetic_score: float = 0.0
    vendor_match: bool = False
    brand_match: bool = False
    type_match: bool = False
    weight_match: bool = False
    strain_match: bool = False
    match_reason: str = ""
    algorithm_used: str = ""

class AdvancedMatcher:
    """
    Advanced matching system that combines multiple algorithms for optimal results.
    """
    
    def __init__(self):
        self.performance_cache = {}
        self.normalization_cache = {}
        self.key_terms_cache = {}
        self.algorithm_weights = {
            'exact': 1.0,
            'fuzzy': 0.8,
            'semantic': 0.7,
            'phonetic': 0.6,
            'vendor': 0.5,
            'brand': 0.4,
            'type': 0.3,
            'weight': 0.2,
            'strain': 0.1
        }
        
        # Performance settings
        self.max_cache_size = 10000
        self.cache_cleanup_threshold = 0.8
        
        # Common words to ignore in matching
        self.common_words = {
            'the', 'and', 'or', 'for', 'with', 'by', 'from', 'to', 'of', 'in', 'on', 'at',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
            'shall', 'a', 'an', 'as', 'if', 'when', 'where', 'why', 'how', 'what', 'who'
        }
        
        # Product type mappings for better matching
        self.product_type_mappings = {
            'flower': ['flower', 'bud', 'nug', 'buds', 'nugs', 'cannabis', 'marijuana'],
            'edible': ['edible', 'gummy', 'gummies', 'chocolate', 'candy', 'cookie', 'brownie'],
            'concentrate': ['concentrate', 'wax', 'shatter', 'rosin', 'live resin', 'distillate'],
            'topical': ['topical', 'cream', 'balm', 'lotion', 'salve', 'ointment'],
            'tincture': ['tincture', 'drops', 'liquid', 'oil'],
            'cartridge': ['cartridge', 'cart', 'vape', 'pen']
        }
        # Common abbreviation/alias map for strain shortcodes -> expanded names
        # Keep keys lowercase and normalized (normalized form produced by normalize_text)
        self.abbreviation_map = {
            'gg4': 'gorilla glue 4',
            'gg#4': 'gorilla glue 4',
            'gg#4': 'gorilla glue 4',
            'gg#1': 'gorilla glue 1',
            'gg': 'gorilla glue',
            'gsc': 'girl scout cookies',
            'bubba': 'bubba kush',
            'skunk1': 'skunk 1',
            'skunk#1': 'skunk 1',
            'alien runtz': 'alien runtz',
            'pure': 'pure',
            'prana': 'prana'
        }
        # Common product-descriptor tokens that are not helpful for strain/brand matching
        self.product_descriptors = {
            'pure', 'live', 'resin', 'disposable', 'vape', 'cartridge', 'cart', 'aio', 'pulse',
            'hybrid', 'indica', 'sativa', '1ml', 'ml', 'g', 'gram', 'grams'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent matching."""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase and strip
        text = text.lower().strip()

        # Merge letter+separator+digits patterns like 'gg#4' or 'gg 4' into 'gg4'
        text = re.sub(r'([a-zA-Z]+)[^0-9a-zA-Z]+(\d+)', r"\1\2", text)

        # Replace common separators that often appear inside model/strain codes
        text = re.sub(r'[\/#@\u2013\u2014]', ' ', text)

        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s-]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        result = text.strip()

        # Expand common abbreviations (e.g., 'gg4' -> 'gorilla glue 4')
        try:
            tokens = result.split()
            expanded = [self.abbreviation_map.get(tok, tok) for tok in tokens]
            # Remove generic product descriptor tokens early to strengthen core name signals
            filtered = [tok for tok in expanded if tok not in self.product_descriptors and tok not in self.common_words]
            result = ' '.join(filtered)
        except Exception:
            pass

        return result

    def extract_strain_tokens(self, text: str):
        """Extract strain-like tokens such as 'skunk #1', 'skunk 1', or 'skunk1'.
        Returns a list of (base, number) tuples. Base and number are lowercased strings.
        """
        if not text or not isinstance(text, str):
            return []

        t = text.lower()
        tokens = []

        try:
            # Patterns to capture base + numeric strain identifiers in several common formats
            patterns = [
                r"\b([a-z]{2,})\s*#\s*(\d{1,3})\b",    # skunk #1
                r"\b([a-z]{2,})[\s-]+(\d{1,3})\b",      # skunk 1 or skunk-1
                r"\b([a-z]{2,})(\d{1,3})\b"              # skunk1
            ]

            for pat in patterns:
                for m in re.finditer(pat, t):
                    base = (m.group(1) or '').strip()
                    num = (m.group(2) or '').strip()
                    if not base or not num:
                        continue
                    # Ignore matches that are clearly units or descriptors
                    if base in self.product_descriptors or base in {'ml', 'g', 'oz', 'gram', 'grams'}:
                        continue
                    tokens.append((base, num))
        except Exception:
            return []

        # Deduplicate while preserving order
        seen = set()
        out = []
        for b, n in tokens:
            key = f"{b}{n}"
            if key not in seen:
                seen.add(key)
                out.append((b, n))
        return out
    
    def _is_vendor_match(self, vendor1: str, vendor2: str) -> bool:
        """Check if two vendor names represent the same vendor using various patterns."""
        if not vendor1 or not vendor2:
            return False
        
        # Remove common business suffixes and variations
        suffixes = [
            'llc', 'inc', 'corp', 'ltd', 'co', 'company', 'holdings', 'group', 'brands',
            'enterprises', 'industries', 'solutions', 'systems', 'services', 'products',
            'farms', 'garden', 'cultivation', 'cannabis', 'hemp', 'marijuana',
            'wholesale', 'distribution', 'supply', 'cooperative', 'collective'
        ]
        
        v1_clean = vendor1.lower().strip()
        v2_clean = vendor2.lower().strip()
        
        # Remove suffixes and clean up
        for suffix in suffixes:
            v1_clean = v1_clean.replace(f' {suffix}', '').replace(f'-{suffix}', '').replace(f'_{suffix}', '')
            v2_clean = v2_clean.replace(f' {suffix}', '').replace(f'-{suffix}', '').replace(f'_{suffix}', '')
        
        # Remove common prefixes
        prefixes = ['the', 'a', 'an']
        for prefix in prefixes:
            if v1_clean.startswith(f'{prefix} '):
                v1_clean = v1_clean[len(prefix)+1:]
            if v2_clean.startswith(f'{prefix} '):
                v2_clean = v2_clean[len(prefix)+1:]
        
        # Clean up extra spaces and special characters
        import re
        v1_clean = re.sub(r'\s+', ' ', v1_clean).strip()
        v2_clean = re.sub(r'\s+', ' ', v2_clean).strip()
        
        # Check if cleaned names match exactly
        if v1_clean == v2_clean:
            return True
        
        # Check for acronym matches (e.g., "CERES" vs "Ceres Holdings")
        if len(v1_clean) <= 6 and len(v2_clean) > 6:
            if v1_clean in v2_clean:
                return True
        elif len(v2_clean) <= 6 and len(v1_clean) > 6:
            if v2_clean in v1_clean:
                return True
        
        # Check for partial matches with high confidence
        if len(v1_clean) >= 3 and len(v2_clean) >= 3:
            # Check if one is a subset of the other
            if v1_clean in v2_clean or v2_clean in v1_clean:
                return True
            
            # Check for word overlap (at least 50% of words match)
            v1_words = set(v1_clean.split())
            v2_words = set(v2_clean.split())
            if len(v1_words) > 0 and len(v2_words) > 0:
                overlap = len(v1_words.intersection(v2_words))
                min_words = min(len(v1_words), len(v2_words))
                if overlap / min_words >= 0.5:
                    return True
            
            # Check for phonetic similarity (Soundex)
            try:
                import jellyfish
                if jellyfish.soundex(v1_clean) == jellyfish.soundex(v2_clean):
                    return True
            except:
                pass
        
        return False
    
    def calculate_ai_powered_scores(self, json_name: str, candidate_name: str, json_item: Dict, candidate: Dict) -> Dict:
        """Calculate AI-powered scores for difficult product name matching."""
        scores = {}
        
        try:
            # 1. N-gram similarity (character-level)
            scores['ngram'] = self._calculate_ngram_similarity(json_name, candidate_name)
            
            # 2. Levenshtein distance ratio
            scores['levenshtein'] = self._calculate_levenshtein_ratio(json_name, candidate_name)
            
            # 3. Jaccard similarity on words
            scores['jaccard'] = self._calculate_jaccard_similarity(json_name, candidate_name)
            
            # 4. Subsequence matching
            scores['subsequence'] = self._calculate_subsequence_score(json_name, candidate_name)
            
            # 5. Soundex similarity
            scores['soundex'] = self._calculate_soundex_similarity(json_name, candidate_name)
            
            # 6. Metaphone similarity
            scores['metaphone'] = self._calculate_metaphone_similarity(json_name, candidate_name)
            
            # 7. Partial string matching
            scores['partial'] = self._calculate_partial_match_score(json_name, candidate_name)
            
            # 8. Keyword extraction and matching
            scores['keywords'] = self._calculate_keyword_similarity(json_name, candidate_name)

            # Build "core" versions of both names with product descriptor tokens removed
            try:
                core_json = ' '.join([t for t in self.normalize_text(json_name).split() if t not in self.product_descriptors])
                core_cand = ' '.join([t for t in self.normalize_text(candidate_name).split() if t not in self.product_descriptors])
            except Exception:
                core_json = self.normalize_text(json_name)
                core_cand = self.normalize_text(candidate_name)

            # Compute core ngram/levenshtein on descriptor-stripped strings to avoid descriptor-driven similarity
            scores['core_ngram'] = self._calculate_ngram_similarity(core_json, core_cand)
            scores['core_levenshtein'] = self._calculate_levenshtein_ratio(core_json, core_cand)
            
            # 8b. Exact token overlap (helps short codes like GG4, Bx3, etc.)
            scores['token_overlap'] = self._calculate_token_overlap_score(json_name, candidate_name)
            
            # 9. Weight/size pattern matching
            scores['weight_pattern'] = self._calculate_weight_pattern_score(json_name, candidate_name)
            
            # 10. Product type pattern matching
            scores['type_pattern'] = self._calculate_type_pattern_score(json_name, candidate_name, json_item, candidate)
            
        except Exception as e:
            logging.debug(f"Error in AI-powered scoring: {e}")
            # Return default scores if there's an error
            scores = {key: 0.0 for key in ['ngram', 'levenshtein', 'jaccard', 'subsequence', 'soundex', 'metaphone', 'partial', 'keywords', 'weight_pattern', 'type_pattern']}
        
        return scores
    
    def calculate_overall_score_with_ai(self, match_result: MatchResult, ai_scores: Dict) -> float:
        """Calculate overall score including AI-powered scores."""
        # Base score from original calculation
        base_score = self.calculate_overall_score(match_result)
        
        # AI score boost (weighted average of AI scores) - more generous
        ai_boost = 0.0
        if ai_scores:
            # Weight different AI algorithms - increased weights for better matching
            weights = {
                'ngram': 0.20,  # Character n-gram similarity
                'levenshtein': 0.20,  # Edit distance
                'jaccard': 0.15,  # Word set similarity
                'subsequence': 0.15,  # Subsequence match
                'soundex': 0.08,  # Phonetic
                'metaphone': 0.07,  # Phonetic
                'partial': 0.12,  # Partial substring matching
                'keywords': 0.12,  # Keyword overlap
                'token_overlap': 0.18,  # Exact token overlap (short codes)
                'weight_pattern': 0.10,  # Numeric weight similarity
                'type_pattern': 0.10  # Product type patterns
            }
            
            weighted_ai_score = sum(ai_scores.get(key, 0) * weight for key, weight in weights.items())
            ai_boost = weighted_ai_score * 0.5  # Increased from 30% to 50% weight for AI scores

            # Compute a focused name-strength metric to avoid high scores when names aren't actually similar
            # Prefer core (descriptor-stripped) name signals when available
            name_components = {
                'ngram': ai_scores.get('core_ngram', ai_scores.get('ngram', 0.0)),
                'levenshtein': ai_scores.get('core_levenshtein', ai_scores.get('levenshtein', 0.0)),
                'token_overlap': ai_scores.get('token_overlap', 0.0),
                'keywords': ai_scores.get('keywords', 0.0),
                'partial': ai_scores.get('partial', 0.0)
            }
            # weighted name strength (sum of component * factor) / total
            name_weights = {'ngram': 0.30, 'levenshtein': 0.20, 'token_overlap': 0.25, 'keywords': 0.15, 'partial': 0.10}
            name_strength = 0.0
            for k, v in name_components.items():
                name_strength += v * name_weights.get(k, 0)

            # If name strength is low, significantly reduce AI boost to avoid false positives
            if name_strength < 30.0:
                ai_boost *= 0.25
                low_name_penalty = True
            else:
                low_name_penalty = False

            # More conservative: if name strength is clearly under a stricter threshold,
            # heavily suppress AI boost so matches with weak name similarity don't score high.
            if name_strength < 40.0:
                ai_boost *= 0.1
                low_name_penalty = True

            # Extra conservative rule: if token overlap and keyword overlap are both weak
            # and core ngram is also modest, strongly suppress AI boost to avoid false positives.
            core_ngram = name_components.get('ngram', 0.0)
            token_ov = name_components.get('token_overlap', 0.0)
            keyword_score = name_components.get('keywords', 0.0)
            if core_ngram < 40.0 and token_ov < 30.0 and keyword_score < 30.0:
                ai_boost *= 0.15
                low_name_penalty = True
        
        # Strict gating: require at least one exact non-descriptor token overlap
        try:
            # Targeted strain extraction: require candidate to include strain base+number
            raw_query = getattr(match_result, 'query_name', '') or ''
            # Candidate name may come under several keys depending on callsite
            cand_raw = ''
            try:
                cand_raw = (match_result.item.get('original_name') or match_result.item.get('Product Name*') or match_result.item.get('product_name') or '')
            except Exception:
                try:
                    cand_raw = str(match_result.item)
                except Exception:
                    cand_raw = ''
            cand_name = self.normalize_text(str(cand_raw))
            strains = self.extract_strain_tokens(raw_query)
            if strains:
                cand_tokens = set(cand_name.split())
                ok = True
                for base, num in strains:
                    combined = f"{base}{num}"
                    # Accept if combined token exists or both base and number appear as tokens
                    if combined in cand_name or (base in cand_tokens and num in cand_tokens):
                        continue
                    ok = False
                    break
                if not ok:
                    # Allow targeted exception when strong other signals indicate match
                    try:
                        # Conditions for exception: weight matches strongly, product type indicates vape/cartridge,
                        # and either token/keyword overlap or strong core name signal exists.
                        wt = ai_scores.get('weight_pattern', 0.0)
                        core_ng = ai_scores.get('core_ngram', ai_scores.get('ngram', 0.0))
                        tok_ov = ai_scores.get('token_overlap', 0.0)
                        kw = ai_scores.get('keywords', 0.0)
                        cand_lower = cand_name.lower()
                        type_like = any(x in cand_lower for x in ('vape', 'cartridge', 'cart', 'disposable', 'pen'))

                        if wt >= 90.0 and core_ng >= 30.0 and type_like and (tok_ov >= 15.0 or kw >= 30.0 or match_result.vendor_match):
                            # Construct a high confidence score when these conditions hold
                            fallback_score = min(100.0, max(95.0, base_score + ai_boost + 10.0))
                            match_result.match_reason = 'Strain missing but weight+type+keywords indicate strong match'
                            return fallback_score
                    except Exception:
                        pass
                    return 0.0
        except Exception:
            pass

        # Combine base score with AI boost
        final_score = base_score + ai_boost
        
        # Ensure minimum score for vendor matches - more generous
        if match_result.vendor_match and final_score < 25:  # Increased from 20
            final_score = max(25, final_score)
        
        # Ensure minimum score for any meaningful match
        if (match_result.vendor_match or match_result.brand_match or match_result.type_match) and final_score < 20:
            final_score = max(20, final_score)
        # If name-based AI signals are very strong, favor them even if other context differs
        if ai_scores:
            name_strength = max(
                ai_scores.get('token_overlap', 0.0),
                ai_scores.get('ngram', 0.0),
                ai_scores.get('levenshtein', 0.0),
                ai_scores.get('keywords', 0.0),
                ai_scores.get('partial', 0.0)
            )
            if name_strength >= 80.0:
                # Blend final score with name strength to favor clear name matches
                final_score = max(final_score, min(100.0, final_score * 0.4 + name_strength * 0.6))

        return min(100.0, final_score)  # Cap at 100
    
    def _calculate_ngram_similarity(self, str1: str, str2: str, n: int = 3) -> float:
        """Calculate n-gram similarity between two strings."""
        try:
            from rapidfuzz import fuzz
            return fuzz.ratio(str1, str2)
        except:
            return 0.0
    
    def _calculate_levenshtein_ratio(self, str1: str, str2: str) -> float:
        """Calculate Levenshtein distance ratio."""
        try:
            from rapidfuzz import fuzz
            return fuzz.ratio(str1, str2)
        except:
            return 0.0
    
    def _calculate_jaccard_similarity(self, str1: str, str2: str) -> float:
        """Calculate Jaccard similarity based on word sets."""
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 and not words2:
            return 100.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return (intersection / union) * 100.0
    
    def _calculate_subsequence_score(self, str1: str, str2: str) -> float:
        """Calculate subsequence matching score."""
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # Check if str1 is a subsequence of str2 or vice versa
        if self._is_subsequence(str1_lower, str2_lower) or self._is_subsequence(str2_lower, str1_lower):
            return 80.0
        
        return 0.0
    
    def _is_subsequence(self, s1: str, s2: str) -> bool:
        """Check if s1 is a subsequence of s2."""
        i = j = 0
        while i < len(s1) and j < len(s2):
            if s1[i] == s2[j]:
                i += 1
            j += 1
        return i == len(s1)
    
    def _calculate_soundex_similarity(self, str1: str, str2: str) -> float:
        """Calculate Soundex similarity."""
        try:
            import jellyfish
            soundex1 = jellyfish.soundex(str1)
            soundex2 = jellyfish.soundex(str2)
            return 100.0 if soundex1 == soundex2 else 0.0
        except:
            return 0.0
    
    def _calculate_metaphone_similarity(self, str1: str, str2: str) -> float:
        """Calculate Metaphone similarity."""
        try:
            import jellyfish
            meta1 = jellyfish.metaphone(str1)
            meta2 = jellyfish.metaphone(str2)
            return 100.0 if meta1 == meta2 else 0.0
        except:
            return 0.0
    
    def _calculate_partial_match_score(self, str1: str, str2: str) -> float:
        """Calculate partial string matching score."""
        str1_lower = str1.lower()
        str2_lower = str2.lower()
        
        # Check for partial matches
        if str1_lower in str2_lower or str2_lower in str1_lower:
            return 70.0
        
        # Check for word-level partial matches
        words1 = str1_lower.split()
        words2 = str2_lower.split()
        
        matches = 0
        for word1 in words1:
            for word2 in words2:
                if len(word1) >= 3 and len(word2) >= 3:
                    if word1 in word2 or word2 in word1:
                        matches += 1
                        break
        
        if words1 and words2:
            return (matches / min(len(words1), len(words2))) * 100.0
        
        return 0.0
    
    def _calculate_keyword_similarity(self, str1: str, str2: str) -> float:
        """Calculate keyword-based similarity."""
        # Extract key terms (remove common words)
        common_words = {'the', 'and', 'or', 'for', 'with', 'by', 'from', 'to', 'of', 'in', 'on', 'at', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'a', 'an', 'as', 'if', 'it', 'this', 'that', 'these', 'those'}
        
        words1 = [w for w in str1.lower().split() if w not in common_words and len(w) >= 3]
        words2 = [w for w in str2.lower().split() if w not in common_words and len(w) >= 3]
        
        if not words1 and not words2:
            return 100.0
        if not words1 or not words2:
            return 0.0
        
        matches = len(set(words1).intersection(set(words2)))
        return (matches / max(len(words1), len(words2))) * 100.0

    def _calculate_token_overlap_score(self, str1: str, str2: str) -> float:
        """Calculate exact token overlap score; helps with short codes like 'GG4'."""
        if not str1 or not str2:
            return 0.0

        t1 = self.normalize_text(str1).split()
        t2 = self.normalize_text(str2).split()

        if not t1 and not t2:
            return 100.0
        if not t1 or not t2:
            return 0.0

        set1 = set(t1)
        set2 = set(t2)
        # Remove generic product descriptor tokens from scoring
        filtered1 = {tok for tok in set1 if tok not in self.product_descriptors}
        filtered2 = {tok for tok in set2 if tok not in self.product_descriptors}
        intersection = filtered1.intersection(filtered2)
        if not intersection:
            # If there are only descriptor overlaps (e.g., 'pure live resin'), de-prioritize
            raw_intersection = set1.intersection(set2)
            if raw_intersection:
                return 20.0  # small score when only generic descriptors overlap
            return 0.0

        # Base score is proportion of overlapping tokens (using filtered sets)
        base = (len(intersection) / max(1, min(len(filtered1), len(filtered2)))) * 100.0

        # Boost short alphanumeric tokens (codes) and tokens containing digits
        boost = 0.0
        for token in intersection:
            if any(ch.isdigit() for ch in token) and len(token) <= 6:
                boost += 10.0
            elif len(token) <= 3:
                boost += 5.0

        score = min(100.0, base + boost)
        return score
    
    def _calculate_weight_pattern_score(self, str1: str, str2: str) -> float:
        """Calculate weight/size pattern matching score."""
        import re

        # Helper to parse weight tuples and convert to grams
        def parse_to_grams(match_tuple):
            # match_tuple may be like ('3.5', 'g')
            try:
                val = float(match_tuple[0])
                unit = match_tuple[1].lower()
                if unit.startswith('g'):
                    return val
                # Treat milliliters as approximate grams (1 mL ~= 1 g)
                if unit.startswith('ml') or unit in ('milliliter', 'millilitre', 'milliliters', 'millilitres'):
                    return val
                if unit.startswith('oz') or unit in ('ounce', 'ounces'):
                    return val * 28.3495
                if unit in ('lb', 'pound', 'pounds'):
                    return val * 453.592
            except Exception:
                return None
            return None

        # Extract weight patterns (e.g., "3.5g", "28g", "1oz", "2oz", "1ml")
        weight_pattern = r'(\d+(?:\.\d+)?)\s*(g|grams|gram|gm|ml|milliliter|millilitre|milliliters|millilitres|oz|ounce|ounces|lb|pound|pounds)'

        weights1 = re.findall(weight_pattern, str1.lower())
        weights2 = re.findall(weight_pattern, str2.lower())

        if not weights1 and not weights2:
            return 50.0  # Neutral score if no weights found
        if not weights1 or not weights2:
            return 0.0

        # Compute numeric similarity for any pair and return the best score
        best_score = 0.0
        for w1 in weights1:
            g1 = parse_to_grams(w1)
            if g1 is None:
                continue
            for w2 in weights2:
                g2 = parse_to_grams(w2)
                if g2 is None:
                    continue
                # If nearly identical (within 5%), full score
                try:
                    rel_diff = abs(g1 - g2) / max(g1, g2)
                except Exception:
                    rel_diff = 1.0

                score = max(0.0, 100.0 * (1.0 - rel_diff))
                # Small tolerance boost if units are the same textually
                if w1[1] == w2[1]:
                    score = min(100.0, score + 5.0)
                if score > best_score:
                    best_score = score

        return best_score if best_score > 0 else 0.0
    
    def _calculate_type_pattern_score(self, str1: str, str2: str, json_item: Dict, candidate: Dict) -> float:
        """Calculate product type pattern matching score."""
        # Extract product types from both items
        json_type = str(json_item.get('product_type', '')).lower()
        candidate_type = str(candidate.get('Product Type*', '')).lower()
        
        if not json_type and not candidate_type:
            return 50.0
        if not json_type or not candidate_type:
            return 0.0
        
        # Check for type matches
        if json_type in candidate_type or candidate_type in json_type:
            return 100.0
        
        # Check for common type patterns
        type_patterns = {
            'flower': ['flower', 'bud', 'buds', 'nugs', 'nuggets'],
            'edible': ['edible', 'gummy', 'gummies', 'chocolate', 'candy', 'cookie', 'brownie'],
            'concentrate': ['concentrate', 'wax', 'shatter', 'rosin', 'live resin', 'bho'],
            'vape': ['vape', 'cartridge', 'cart', 'disposable', 'pen'],
            'pre-roll': ['pre-roll', 'preroll', 'joint', 'blunt', 'cigarillo']
        }
        
        for category, patterns in type_patterns.items():
            json_has_pattern = any(pattern in json_type for pattern in patterns)
            candidate_has_pattern = any(pattern in candidate_type for pattern in patterns)
            
            if json_has_pattern and candidate_has_pattern:
                return 100.0
        
        return 0.0
    
    def _cleanup_cache(self):
        """Clean up caches when they get too large."""
        if len(self.performance_cache) > self.max_cache_size * self.cache_cleanup_threshold:
            # Remove oldest 20% of entries
            items_to_remove = int(len(self.performance_cache) * 0.2)
            keys_to_remove = list(self.performance_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.performance_cache[key]
        
        if len(self.normalization_cache) > self.max_cache_size * self.cache_cleanup_threshold:
            items_to_remove = int(len(self.normalization_cache) * 0.2)
            keys_to_remove = list(self.normalization_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.normalization_cache[key]
        
        if len(self.key_terms_cache) > self.max_cache_size * self.cache_cleanup_threshold:
            items_to_remove = int(len(self.key_terms_cache) * 0.2)
            keys_to_remove = list(self.key_terms_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.key_terms_cache[key]
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent matching with caching."""
        if not isinstance(text, str):
            return ""
        
        # Check cache first
        if text in self.normalization_cache:
            return self.normalization_cache[text]
        
        # Convert to lowercase and strip
        normalized = text.lower().strip()

        # Merge letter+separator+digits patterns like 'gg#4' or 'gg 4' into 'gg4'
        normalized = re.sub(r'([a-zA-Z]+)[^0-9a-zA-Z]+(\d+)', r"\1\2", normalized)

        # Replace common separators that often appear inside model/strain codes
        normalized = re.sub(r'[\/#@\u2013\u2014]', ' ', normalized)

        # Remove special characters but keep spaces and hyphens
        normalized = re.sub(r'[^\w\s-]', ' ', normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        result = normalized.strip()
        
        # Cache the result
        self.normalization_cache[text] = result
        
        # Cleanup cache if needed
        self._cleanup_cache()
        
        return result
    
    def extract_key_terms(self, text: str) -> Set[str]:
        """Extract meaningful key terms from text with caching."""
        if not text:
            return set()
        
        # Check cache first
        if text in self.key_terms_cache:
            return self.key_terms_cache[text]
        
        normalized = self.normalize_text(text)
        words = set(normalized.split())
        
        # Filter out common words and short words
        key_terms = {
            word for word in words 
            if len(word) > 2 and word not in self.common_words and word not in self.product_descriptors
        }
        
        # Cache the result
        self.key_terms_cache[text] = key_terms
        
        # Cleanup cache if needed
        self._cleanup_cache()
        
        return key_terms
    
    def calculate_fuzzy_score(self, text1: str, text2: str) -> Tuple[float, str]:
        """Calculate fuzzy matching score using the best available algorithm with caching."""
        if not text1 or not text2:
            return 0.0, "no_text"
        
        # Create cache key
        cache_key = f"{text1}|{text2}"
        if cache_key in self.performance_cache:
            return self.performance_cache[cache_key]
        
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        if text1_norm == text2_norm:
            result = (100.0, "exact")
            self.performance_cache[cache_key] = result
            return result
        
        scores = []
        algorithms = []
        
        # Try RapidFuzz first (fastest and most accurate)
        if RAPIDFUZZ_AVAILABLE:
            try:
                ratio = rapidfuzz_fuzz.ratio(text1_norm, text2_norm)
                partial_ratio = rapidfuzz_fuzz.partial_ratio(text1_norm, text2_norm)
                token_sort_ratio = rapidfuzz_fuzz.token_sort_ratio(text1_norm, text2_norm)
                token_set_ratio = rapidfuzz_fuzz.token_set_ratio(text1_norm, text2_norm)
                
                # Use the best score from RapidFuzz
                best_score = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
                scores.append(best_score)
                algorithms.append("rapidfuzz")
            except Exception as e:
                logging.warning(f"RapidFuzz error: {e}")
        
        # Fallback to FuzzyWuzzy
        if FUZZYWUZZY_AVAILABLE:
            try:
                ratio = fuzzywuzzy_fuzz.ratio(text1_norm, text2_norm)
                partial_ratio = fuzzywuzzy_fuzz.partial_ratio(text1_norm, text2_norm)
                token_sort_ratio = fuzzywuzzy_fuzz.token_sort_ratio(text1_norm, text2_norm)
                token_set_ratio = fuzzywuzzy_fuzz.token_set_ratio(text1_norm, text2_norm)
                
                best_score = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
                scores.append(best_score)
                algorithms.append("fuzzywuzzy")
            except Exception as e:
                logging.warning(f"FuzzyWuzzy error: {e}")
        
        # Fallback to difflib
        if DIFFLIB_AVAILABLE and not scores:
            try:
                matcher = difflib.SequenceMatcher(None, text1_norm, text2_norm)
                score = matcher.ratio() * 100
                scores.append(score)
                algorithms.append("difflib")
            except Exception as e:
                logging.warning(f"difflib error: {e}")
        
        if scores:
            best_score = max(scores)
            best_algorithm = algorithms[scores.index(best_score)]
            result = (best_score, best_algorithm)
            self.performance_cache[cache_key] = result
            return result
        
        result = (0.0, "none")
        self.performance_cache[cache_key] = result
        return result
    
    def calculate_phonetic_score(self, text1: str, text2: str) -> float:
        """Calculate phonetic similarity using Jellyfish algorithms."""
        if not JELLYFISH_AVAILABLE or not text1 or not text2:
            return 0.0
        
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        if text1_norm == text2_norm:
            return 100.0
        
        try:
            # Jaro-Winkler similarity (good for names)
            jaro_winkler = jellyfish.jaro_winkler_similarity(text1_norm, text2_norm)
            
            # Soundex comparison
            soundex1 = jellyfish.soundex(text1_norm)
            soundex2 = jellyfish.soundex(text2_norm)
            soundex_match = 100.0 if soundex1 == soundex2 else 0.0
            
            # Metaphone comparison
            metaphone1 = jellyfish.metaphone(text1_norm)
            metaphone2 = jellyfish.metaphone(text2_norm)
            metaphone_match = 100.0 if metaphone1 == metaphone2 else 0.0
            
            # Average the phonetic scores
            phonetic_score = (jaro_winkler * 100 + soundex_match + metaphone_match) / 3
            return phonetic_score
            
        except Exception as e:
            logging.warning(f"Phonetic matching error: {e}")
            return 0.0
    
    def calculate_semantic_score(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity based on key terms and context."""
        if not text1 or not text2:
            return 0.0
        
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        if text1_norm == text2_norm:
            return 100.0
        
        # Extract key terms
        terms1 = self.extract_key_terms(text1)
        terms2 = self.extract_key_terms(text2)
        
        if not terms1 or not terms2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(terms1.intersection(terms2))
        union = len(terms1.union(terms2))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Weight by term importance (longer terms are more important)
        weighted_score = 0.0
        total_weight = 0.0
        
        for term in terms1.intersection(terms2):
            weight = len(term)  # Longer terms get more weight
            weighted_score += weight
            total_weight += weight
        
        if total_weight > 0:
            weighted_similarity = weighted_score / total_weight
            # Combine Jaccard and weighted similarity
            semantic_score = (jaccard_similarity * 0.7 + weighted_similarity * 0.3) * 100
        else:
            semantic_score = jaccard_similarity * 100
        
        return semantic_score
    
    def calculate_contextual_scores(self, json_item: Dict, cache_item: Dict) -> Dict[str, float]:
        """Calculate contextual matching scores for various attributes."""
        scores = {}
        
        # Vendor matching
        json_vendor = self.normalize_text(str(json_item.get("vendor", "")))
        cache_vendor = self.normalize_text(str(cache_item.get("vendor", "")))
        if json_vendor and cache_vendor:
            vendor_fuzzy, _ = self.calculate_fuzzy_score(json_vendor, cache_vendor)
            scores['vendor'] = vendor_fuzzy
        else:
            scores['vendor'] = 0.0
        
        # Brand matching
        json_brand = self.normalize_text(str(json_item.get("brand", "")))
        cache_brand = self.normalize_text(str(cache_item.get("brand", "")))
        if json_brand and cache_brand:
            brand_fuzzy, _ = self.calculate_fuzzy_score(json_brand, cache_brand)
            scores['brand'] = brand_fuzzy
        else:
            scores['brand'] = 0.0
        
        # Product type matching
        json_type = self.normalize_text(str(json_item.get("product_type", "")))
        cache_type = self.normalize_text(str(cache_item.get("product_type", "")))
        if json_type and cache_type:
            type_fuzzy, _ = self.calculate_fuzzy_score(json_type, cache_type)
            scores['type'] = type_fuzzy
        else:
            scores['type'] = 0.0
        
        # Weight matching
        json_weight = self.normalize_text(str(json_item.get("weight", "")))
        cache_weight = self.normalize_text(str(cache_item.get("weight", "")))
        if json_weight and cache_weight:
            weight_fuzzy, _ = self.calculate_fuzzy_score(json_weight, cache_weight)
            scores['weight'] = weight_fuzzy
        else:
            scores['weight'] = 0.0
        
        # Strain matching
        json_strain = self.normalize_text(str(json_item.get("strain_name", "")))
        cache_strain = self.normalize_text(str(cache_item.get("strain_name", "")))
        if json_strain and cache_strain:
            strain_fuzzy, _ = self.calculate_fuzzy_score(json_strain, cache_strain)
            scores['strain'] = strain_fuzzy
        else:
            scores['strain'] = 0.0
        
        return scores
    
    def calculate_overall_score(self, match_result: MatchResult) -> float:
        """Calculate overall matching score using weighted algorithm."""
        if match_result.exact_match:
            return 100.0
        
        # Start with fuzzy score as base - ensure minimum score
        base_score = max(10.0, match_result.fuzzy_score)  # Ensure minimum 10 points
        
        # Apply semantic and phonetic scores more heavily
        semantic_contribution = max(5.0, match_result.semantic_score * 0.4)  # Increased weight and minimum
        phonetic_contribution = max(3.0, match_result.phonetic_score * 0.3)  # Increased weight and minimum
        
        # Apply contextual bonuses (much more generous for better matching)
        contextual_bonus = 0.0
        if match_result.vendor_match:
            contextual_bonus += 60  # Even more generous for vendor matching
        if match_result.brand_match:
            contextual_bonus += 25  # Increased from 20
        if match_result.type_match:
            contextual_bonus += 20  # Increased from 15
        if match_result.weight_match:
            contextual_bonus += 15  # Increased from 10
        if match_result.strain_match:
            contextual_bonus += 12  # Increased from 8
        
        # Calculate final score with much more generous weighting
        final_score = min(100.0, base_score + semantic_contribution + phonetic_contribution + contextual_bonus)
        
        # Ensure minimum score for any match with contextual bonuses (much more generous)
        if contextual_bonus > 0 and final_score < 30:  # Increased from 20
            final_score = max(30, final_score)
        
        # Extra bonus for vendor matches to ensure they get through
        if match_result.vendor_match and final_score < 25:  # Increased from 15
            final_score = max(25, final_score)
        
        # Additional boost for any meaningful match
        if (match_result.vendor_match or match_result.brand_match or match_result.type_match) and final_score < 20:
            final_score = max(20, final_score)
        
        return final_score
    
    def find_best_matches(self, json_item: Dict, candidates: List[Dict], 
                         threshold: float = 1.0, max_results: int = 50) -> List[MatchResult]:
        """Find the best matches for a JSON item from a list of candidates."""
        if not json_item or not candidates:
            return []
        
        json_name = str(json_item.get("product_name", "")).strip()
        json_vendor = self.normalize_text(str(json_item.get("vendor", "")).strip())
        
        if not json_name:
            return []
        
        matches = []
        start_time = time.time()
        
        # Filter candidates by vendor first (if vendor is specified)
        filtered_candidates = candidates
        if json_vendor:
            filtered_candidates = []
            vendor_matches = 0
            total_candidates = len(candidates)
            
            print(f"🔍 ADVANCED VENDOR FILTERING: Looking for vendor '{json_vendor}' in {total_candidates} candidates")
            
            # Show some sample candidates for debugging
            if total_candidates > 0:
                sample_candidates = candidates[:5]
                print(f"🔍 SAMPLE CANDIDATES:")
                for i, candidate in enumerate(sample_candidates):
                    candidate_name = str(candidate.get("original_name", "")).strip()
                    candidate_vendor = str(candidate.get("vendor", "")).strip()
                    print(f"  {i+1}. '{candidate_name}' (vendor: '{candidate_vendor}')")
            
            for candidate in candidates:
                candidate_vendor = self.normalize_text(str(candidate.get("vendor", "")).strip())
                
                # Enhanced flexible vendor matching - check all variations
                vendor_match = False
                if candidate_vendor and json_vendor:
                    # Normalize both vendors for comparison
                    json_vendor_clean = self.normalize_text(json_vendor)
                    candidate_vendor_clean = self.normalize_text(candidate_vendor)
                    
                    # 1. Exact match after normalization
                    if json_vendor_clean == candidate_vendor_clean:
                        vendor_match = True
                    # 2. One contains the other (for cases like "CERES" vs "CERES - 435011")
                    elif json_vendor_clean in candidate_vendor_clean or candidate_vendor_clean in json_vendor_clean:
                        vendor_match = True
                    # 3. Word overlap (at least 50% of words match)
                    elif len(json_vendor_clean.split()) > 0 and len(candidate_vendor_clean.split()) > 0:
                        json_words = set(json_vendor_clean.split())
                        candidate_words = set(candidate_vendor_clean.split())
                        overlap = len(json_words.intersection(candidate_words))
                        min_words = min(len(json_words), len(candidate_words))
                        if overlap / min_words >= 0.5:
                            vendor_match = True
                    # 4. Fuzzy matching for similar names (more lenient for vendor names)
                    elif len(json_vendor_clean) >= 3 and len(candidate_vendor_clean) >= 3:  # Reduced from 4 to 3
                        try:
                            from rapidfuzz import fuzz
                            vendor_ratio = fuzz.ratio(json_vendor_clean, candidate_vendor_clean)
                            partial_ratio = fuzz.partial_ratio(json_vendor_clean, candidate_vendor_clean)
                            # Use the higher of the two ratios and lower threshold
                            best_ratio = max(vendor_ratio, partial_ratio)
                            if best_ratio >= 60:  # Reduced from 70 to 60 for more lenient matching
                                vendor_match = True
                        except:
                            pass
                    # 5. Check for common vendor name patterns
                    elif self._is_vendor_match_flexible(json_vendor_clean, candidate_vendor_clean):
                        vendor_match = True
                
                if vendor_match:
                    filtered_candidates.append(candidate)
                    vendor_matches += 1
                    if vendor_matches <= 3:  # Log first 3 matches
                        print(f"🔍 ADVANCED VENDOR MATCH {vendor_matches}: '{json_vendor}' matches '{candidate_vendor}'")
                elif candidate_vendor:  # Log first few non-matches
                    if vendor_matches < 3:
                        print(f"🔍 ADVANCED VENDOR SKIP: '{json_vendor}' != '{candidate_vendor}'")
            
            # If still no vendor matches found, attempt flexible vendor resolution without crossing vendors
            if not filtered_candidates:
                # Show what vendors are actually available
                available_vendors = set()
                for candidate in candidates[:50]:  # Check first 50 candidates
                    candidate_vendor = str(candidate.get("vendor", "")).strip()
                    if candidate_vendor:
                        available_vendors.add(candidate_vendor)
                
                print(f"🔍 ADVANCED VENDOR: No vendor matches found for '{json_vendor}'")
                print(f"🔍 AVAILABLE VENDORS: {sorted(list(available_vendors))[:20]}...")
                print(f"🔍 ADVANCED VENDOR: No vendor matches found - attempting flexible vendor lookup")
                
                # DEBUG: Try to find any vendor that might match using flexible matching
                print(f"🔍 DEBUG: Looking for flexible matches to '{json_vendor}'...")
                potential_matches = []
                json_vendor_clean = self.normalize_text(json_vendor)
                
                for vendor in sorted(list(available_vendors)):
                    vendor_clean = self.normalize_text(vendor)
                    
                    # Check for various matching patterns
                    is_match = False
                    match_reason = ""
                    
                    # 1. Exact match after normalization
                    if json_vendor_clean == vendor_clean:
                        is_match = True
                        match_reason = "exact normalized"
                    
                    # 2. One contains the other
                    elif json_vendor_clean in vendor_clean or vendor_clean in json_vendor_clean:
                        is_match = True
                        match_reason = "contains"
                    
                    # 3. Word overlap (at least 50% of words match)
                    elif len(json_vendor_clean.split()) > 0 and len(vendor_clean.split()) > 0:
                        json_words = set(json_vendor_clean.split())
                        vendor_words = set(vendor_clean.split())
                        overlap = len(json_words.intersection(vendor_words))
                        min_words = min(len(json_words), len(vendor_words))
                        if overlap / min_words >= 0.5:
                            is_match = True
                            match_reason = f"word overlap ({overlap}/{min_words})"
                    
                    # 4. Fuzzy matching for similar names
                    elif len(json_vendor_clean) >= 4 and len(vendor_clean) >= 4:
                        try:
                            from rapidfuzz import fuzz
                            ratio = fuzz.ratio(json_vendor_clean, vendor_clean)
                            if ratio >= 70:  # 70% similarity threshold
                                is_match = True
                                match_reason = f"fuzzy ({ratio}%)"
                        except:
                            pass
                    
                    # 5. Check for common business name patterns
                    elif self._is_vendor_match_flexible(json_vendor_clean, vendor_clean):
                        is_match = True
                        match_reason = "business pattern"
                    
                    if is_match:
                        potential_matches.append(vendor)
                        print(f"🔍 DEBUG: POTENTIAL MATCH: '{json_vendor}' vs '{vendor}' ({match_reason})")
                
                # If we found potential matches, use them, otherwise stop matching
                if potential_matches:
                    print(f"🔍 DEBUG: Found {len(potential_matches)} potential CERES matches, using them")
                    filtered_candidates = [
                        candidate
                        for candidate in candidates
                        if str(candidate.get("vendor", "")).strip() in potential_matches
                    ]
                    print(f"🔍 DEBUG: Filtered to {len(filtered_candidates)} candidates from potential CERES vendors")
                else:
                    print(f"🔍 DEBUG: No vendor matches found in Excel data - aborting to prevent cross-vendor matches")
                    return []
            else:
                print(f"🔍 ADVANCED VENDOR: Filtered to {len(filtered_candidates)} candidates from same vendor '{json_vendor}' (found {vendor_matches} vendor matches)")
        
        for candidate in filtered_candidates:
            candidate_name = str(candidate.get("original_name", "")).strip()
            if not candidate_name:
                continue

            # Strict pre-filter: if JSON name contains a strain-like token (e.g., 'skunk #1'),
            # skip candidates that do not contain that token to enforce exact-description requirement.
            try:
                # Use the extract_strain_tokens helper to find strain-like tokens
                strains = self.extract_strain_tokens(json_name)
                if strains:
                    # Determine whether candidate contains required strain tokens but do not skip here.
                    # Final gating/exception logic will be applied later in calculate_overall_score_with_ai.
                    cand_norm = self.normalize_text(candidate_name)
                    cand_tokens = set(cand_norm.split())
                    ok = True
                    for base, num in strains:
                        combined = f"{base}{num}"
                        if combined in cand_norm or (base in cand_tokens and num in cand_tokens):
                            continue
                        ok = False
                        break
                    # store a flag on candidate dict to indicate strain requirement (optional)
                    try:
                        candidate['_strain_requirement'] = {'present': ok, 'tokens': strains}
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Check for exact match first
            if self.normalize_text(json_name) == self.normalize_text(candidate_name):
                match_result = MatchResult(
                    item=candidate,
                    overall_score=100.0,
                    exact_match=True,
                    fuzzy_score=100.0,
                    match_reason="Exact name match",
                    algorithm_used="exact"
                )
                matches.append(match_result)
                continue
            
            # Calculate fuzzy score
            fuzzy_score, algorithm = self.calculate_fuzzy_score(json_name, candidate_name)
            # Don't skip based on fuzzy score alone - let overall score decide
            
            # Calculate semantic score
            semantic_score = self.calculate_semantic_score(json_name, candidate_name)
            
            # Calculate phonetic score
            phonetic_score = self.calculate_phonetic_score(json_name, candidate_name)
            
            # AI-POWERED DIFFICULT MATCHING: Additional algorithms for hard cases
            ai_scores = self.calculate_ai_powered_scores(json_name, candidate_name, json_item, candidate)
            
            # Calculate contextual scores
            contextual_scores = self.calculate_contextual_scores(json_item, candidate)
            
            # Create match result
            match_result = MatchResult(
                item=candidate,
                overall_score=0.0,  # Will be calculated
                exact_match=False,
                fuzzy_score=fuzzy_score,
                semantic_score=semantic_score,
                phonetic_score=phonetic_score,
                vendor_match=contextual_scores['vendor'] > 80,
                brand_match=contextual_scores['brand'] > 80,
                type_match=contextual_scores['type'] > 80,
                weight_match=contextual_scores['weight'] > 80,
                strain_match=contextual_scores['strain'] > 80,
                match_reason=f"AI-powered match using {algorithm}",
                algorithm_used=algorithm
            )
            # Attach the original JSON query name to the result for gating rules
            try:
                match_result.query_name = json_name
            except Exception:
                match_result.query_name = ''
            
            # Add AI scores to match result
            match_result.ai_scores = ai_scores
            
            # Calculate overall score with AI enhancement
            match_result.overall_score = self.calculate_overall_score_with_ai(match_result, ai_scores)
            
            # Debug logging for first few candidates
            if len(matches) < 3:  # Only log first few to avoid spam
                logging.debug(f"🔍 ADVANCED DEBUG: '{json_name}' vs '{candidate_name}' - fuzzy: {fuzzy_score:.1f}, semantic: {semantic_score:.1f}, phonetic: {phonetic_score:.1f}, overall: {match_result.overall_score:.1f}")
            
            if match_result.overall_score >= threshold:
                matches.append(match_result)
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Limit results
        matches = matches[:max_results]
        
        # Log performance
        elapsed_time = time.time() - start_time
        logging.debug(f"Advanced matching completed in {elapsed_time:.3f}s, found {len(matches)} matches")
        
        return matches
    
    def get_matching_stats(self) -> Dict[str, any]:
        """Get statistics about the matching system."""
        return {
            'libraries_available': {
                'rapidfuzz': RAPIDFUZZ_AVAILABLE,
                'fuzzywuzzy': FUZZYWUZZY_AVAILABLE,
                'jellyfish': JELLYFISH_AVAILABLE,
                'difflib': DIFFLIB_AVAILABLE
            },
            'algorithm_weights': self.algorithm_weights,
            'cache_sizes': {
                'performance_cache': len(self.performance_cache),
                'normalization_cache': len(self.normalization_cache),
                'key_terms_cache': len(self.key_terms_cache)
            },
            'total_cache_size': len(self.performance_cache) + len(self.normalization_cache) + len(self.key_terms_cache),
            'max_cache_size': self.max_cache_size
        }
    
    def clear_caches(self):
        """Clear all caches to free memory."""
        self.performance_cache.clear()
        self.normalization_cache.clear()
        self.key_terms_cache.clear()
        logging.info("All matching caches cleared")
