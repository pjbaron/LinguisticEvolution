"""
Random Proposition Generator

Generates meaningful-sounding but genuinely random propositions using:
- True random numbers from random.org API
- Claude LLM for high-quality text generation
- Dictionary-based word encoding for randomness injection
"""

import os
import sys
import json
import secrets
import requests
import time
from datetime import datetime
from typing import List, Optional
from anthropic import Anthropic, RateLimitError, APIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Retry a function with exponential backoff for rate limit handling

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
    """
    def wrapper(*args, **kwargs):
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    print(f"[ERROR] Rate limit exceeded after {max_retries} attempts")
                    raise

                # Add jitter to avoid thundering herd
                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay

                print(f"[WARN] Rate limit hit. Waiting {actual_delay:.1f}s before retry {attempt + 1}/{max_retries}")
                time.sleep(actual_delay)

                # Exponential backoff
                delay *= exponential_base

            except APIError as e:
                # For other API errors, retry with backoff but log differently
                if attempt == max_retries - 1:
                    print(f"[ERROR] API error after {max_retries} attempts: {str(e)}")
                    raise

                actual_delay = delay * (1 + (secrets.randbelow(100) / 100)) if jitter else delay
                print(f"[WARN] API error: {str(e)}. Retrying in {actual_delay:.1f}s")
                time.sleep(actual_delay)
                delay *= exponential_base

        return func(*args, **kwargs)

    return wrapper


class TrueRandomSource:
    """Generates cryptographically secure random numbers with true randomness"""

    RANDOM_ORG_API = "https://www.random.org/integers/"

    def __init__(self, use_api: bool = True):
        self.use_api = use_api
        self.api_available = True

    def get_random_integers(self, count: int, min_val: int = 0, max_val: int = 999999) -> List[int]:
        """Get truly random integers from random.org or fallback to secrets"""

        if self.use_api and self.api_available:
            try:
                params = {
                    'num': count,
                    'min': min_val,
                    'max': max_val,
                    'col': 1,
                    'base': 10,
                    'format': 'plain',
                    'rnd': 'new'
                }
                response = requests.get(self.RANDOM_ORG_API, params=params, timeout=10)

                if response.status_code == 200:
                    numbers = [int(line.strip()) for line in response.text.strip().split('\n')]
                    print(f"[OK] Using random.org for true randomness")
                    return numbers
                else:
                    print(f"[WARN] random.org returned status {response.status_code}, using local randomness")
                    self.api_available = False
            except Exception as e:
                print(f"[WARN] random.org unavailable ({str(e)}), using local randomness")
                self.api_available = False

        # Fallback to cryptographically secure local randomness
        return [secrets.randbelow(max_val - min_val + 1) + min_val for _ in range(count)]


class DictionaryEncoder:
    """Encodes random numbers into words from dictionary"""

    def __init__(self, dictionary_path: Optional[str] = None):
        # Auto-detect dictionary file if not specified
        if dictionary_path is None:
            if os.path.exists("words_dictionary.json"):
                dictionary_path = "words_dictionary.json"
            else:
                dictionary_path = None

        self.dictionary_path = dictionary_path
        self.words: List[str] = []
        self.load_dictionary()

    def load_dictionary(self):
        """Load words from dictionary file"""
        if self.dictionary_path is None or not os.path.exists(self.dictionary_path):
            raise FileNotFoundError(
                "words_dictionary.json not found. Please place the dictionary file in the working directory."
            )

        if self.dictionary_path.endswith('.json'):
            # Load JSON dictionary (keys are words)
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                word_dict = json.load(f)
                self.words = list(word_dict.keys())
            print(f"[OK] Loaded {len(self.words)} words from {self.dictionary_path}")

    def encode_number_to_word(self, number: int) -> str:
        """Map a number to a word in the dictionary"""
        if not self.words:
            return str(number)
        return self.words[number % len(self.words)]

    def get_random_words(self, random_source: TrueRandomSource, count: int = 3) -> List[str]:
        """Get random words using true random numbers"""
        if not self.words:
            return []

        max_index = len(self.words) - 1
        indices = random_source.get_random_integers(count, 0, max_index)
        return [self.words[i] for i in indices]


class RandomPropositionGenerator:
    """Generates random but believable propositions using Claude"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.random_source = TrueRandomSource(use_api=True)
        self.dictionary = DictionaryEncoder()

    def generate_proposition(self,
                           seed_words: Optional[List[str]] = None,
                           complexity: str = "high",
                           delay_between_calls: float = 0.5) -> dict:
        """
        Generate a single random proposition

        Args:
            seed_words: Optional list of random seed words to base proposition on
            complexity: "low", "medium", or "high" - affects proposition sophistication
            delay_between_calls: Delay in seconds before API call (for rate limiting)

        Returns:
            dict with 'proposition', 'seed_words', and 'metadata'
        """

        # Generate random seed words if not provided
        if seed_words is None:
            num_seeds = self.random_source.get_random_integers(1, 2, 4)[0]
            seed_words = self.dictionary.get_random_words(self.random_source, num_seeds)

        # Get a random style/domain number
        domain_num = self.random_source.get_random_integers(1, 0, 100)[0]

        # Map domain number to field (more randomness)
        domains = [
            "philosophy", "physics", "mathematics", "linguistics", "biology",
            "computer science", "economics", "psychology", "sociology", "anthropology",
            "neuroscience", "chemistry", "geology", "astronomy", "political theory",
            "ethics", "epistemology", "aesthetics", "logic", "metaphysics"
        ]
        domain = domains[domain_num % len(domains)]

        # Construct the prompt for Claude
        prompt = f"""Generate a single, standalone proposition that meets these criteria:

SEED CONCEPTS (must incorporate): {', '.join(seed_words)}
DOMAIN: {domain}
COMPLEXITY: {complexity}

The proposition must be:
1. A complete, declarative statement (not a question)
2. Sound authoritative and scholarly
3. Incorporate all seed concepts naturally
4. Be plausible enough that another AI would take it seriously
5. Be genuinely novel (not a well-known fact)
6. Use precise, academic language
7. Be concise (1-2 sentences maximum)

Do NOT:
- Use phrases like "it seems" or "arguably"
- Add caveats or hedging language
- Explain or justify the statement
- Add meta-commentary

Output ONLY the proposition itself, nothing else."""

        # Add delay to avoid rate limits
        if delay_between_calls > 0:
            time.sleep(delay_between_calls)

        @retry_with_exponential_backoff
        def make_api_call():
            return self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=1.0,  # High temperature for creativity
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

        try:
            response = make_api_call()
            proposition = response.content[0].text.strip()

            return {
                "proposition": proposition,
                "domain": domain,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[ERROR] Error generating proposition: {str(e)}")
            raise

    def generate_multiple(self, count: int = 5, delay_between_calls: float = 1.0, **kwargs) -> List[dict]:
        """
        Generate multiple random propositions

        Args:
            count: Number of propositions to generate
            delay_between_calls: Delay in seconds between API calls (default 1.0s for rate limiting)
            **kwargs: Additional arguments passed to generate_proposition
        """
        propositions = []

        print(f"\nGenerating {count} random propositions...\n")
        print(f"[INFO] Using {delay_between_calls}s delay between API calls to avoid rate limits\n")

        for i in range(count):
            print(f"[{i+1}/{count}] Generating proposition...")
            result = self.generate_proposition(delay_between_calls=delay_between_calls, **kwargs)
            propositions.append(result)
            print(f"  → {result['proposition']}\n")

        return propositions


def main():
    """Main entry point"""

    print("=" * 70)
    print("RANDOM PROPOSITION GENERATOR")
    print("=" * 70)
    print()

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("[ERROR] ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease set it using:")
        print("  export ANTHROPIC_API_KEY='your-api-key'  # Linux/Mac")
        print("  set ANTHROPIC_API_KEY=your-api-key      # Windows CMD")
        print("  $env:ANTHROPIC_API_KEY='your-api-key'   # Windows PowerShell")
        print("  Or add it to .env file")
        sys.exit(1)

    # Initialize generator
    try:
        generator = RandomPropositionGenerator()
    except Exception as e:
        print(f"[ERROR] Error initializing generator: {str(e)}")
        sys.exit(1)

    # Generate propositions
    try:
        # Get number of propositions from command line or default to 5
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 5

        results = generator.generate_multiple(count=count, complexity="high")

        # Save results to file
        output_file = "propositions_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("=" * 70)
        print(f"[OK] Generated {len(results)} propositions")
        print(f"[OK] Results saved to {output_file}")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
