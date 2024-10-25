import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    p = joint_probability(
        people={'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James'},
                'Aykut': {'name': 'Aykut', 'mother': 'Lily', 'father': 'James'},
                'Olesia': {'name': 'Olesia', 'mother': 'Lily', 'father': 'James'},
                'Molly': {'name': 'Molly', 'mother': 'Lily', 'father': 'James'},
                'James': {'name': 'James', 'mother': None, 'father': None},
                'Lily': {'name': 'Lily', 'mother': None, 'father': None}},
        one_gene={'Aykut', 'Olesia', 'Molly', 'Harry'},
        two_genes={},
        have_trait={}
    )

    """
    0.44 * 0.44 * 0.44 * 0.44 * 0.01 * 0.99 * 2 * 0.01 * 0.99 * 2 * 0.03 * 0.03
    2,2 + 2,1 + 1,2 + 1,1
    0.0003 + 0.0003 + 0.0001 + 0.0009

    james 0.03 * 0.44
    lily 0.01 * 0.35
    aykut 0.99 * 0.99 * 0.35
    p(a2 | james1, lily2) = p(a2 ^ james1, lily2) / p(james1, lily2) = 0.03 * 0.01 * 0.99 * 0.99 /
    harry 0.01 * 0.99 * 2 * 0.44"""

    print(f"{p:.15f}")

    sys.exit()

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # print(people)
    # print(one_gene)
    # print(two_genes)
    # print(have_trait)

    joint_probability_var = None

    for k, v in people.items():

        # print(f"{k}, {v}")

        # to have copy_of_genes many genes:
        #   for 0,  mother have father have (mutation * mutation),
        #           mother have father not (mutation * (1 - mutation)),
        #           mother not father have (mutation * (1 - mutation)),
        #           mother not father not (1 - mutation * 1 - mutation)
        #
        #   for 1,  mother have father have (mutation * (1 - mutation) + (1 - mutation) * mutation),
        #           mother have father not ((1 - mutation) * (1 - mutation) + mutation * mutation),
        #           mother not father have ((1 - mutation) * (1 - mutation) + mutation * mutation),
        #           mother not father not (mutation * (1 - mutation)) + (1 - mutation) * mutation)
        #
        #   for 2,  mother have father have ((1 - mutation) * (1 - mutation)),
        #           mother have father not ((1 - mutation) * mutation),
        #           mother not father have ((1 - mutation) * mutation),
        #           mother not father not (mutation * mutation)

        probability_copy_of_genes = None
        probability_trait = None

        if k in one_gene:
            # probability trait
            if k in have_trait:
                probability_trait = PROBS["trait"][1][True]
            else:
                probability_trait = PROBS["trait"][1][False]

            # probability of genes conditional or unconditional
            if v["father"] == None:
                probability_copy_of_genes = PROBS["gene"][1]
            else:
                probability_father_passes = None
                if v["father"] in one_gene:
                    probability_father_passes = 0.5
                elif v["father"] in two_genes:
                    probability_father_passes = (1 - PROBS["mutation"])
                else:
                    probability_father_passes = PROBS["mutation"]

                probability_mother_passes = None
                if v["mother"] in one_gene:
                    probability_mother_passes = 0.5
                elif v["mother"] in two_genes:
                    probability_mother_passes = (1 - PROBS["mutation"])
                else:
                    probability_mother_passes = PROBS["mutation"]

                probability_copy_of_genes = (probability_father_passes * (1 - probability_mother_passes)) + ((1 - probability_father_passes) * probability_mother_passes)

        elif k in two_genes:
            # probability trait
            if k in have_trait:
                probability_trait = PROBS["trait"][2][True]
            else:
                probability_trait = PROBS["trait"][2][False]

            # probability of genes conditional or unconditional
            if v["father"] == None:
                probability_copy_of_genes = PROBS["gene"][2]
            else:
                probability_father_passes = None
                if v["father"] in one_gene:
                    probability_father_passes = 0.5
                elif v["father"] in two_genes:
                    probability_father_passes = (1 - PROBS["mutation"])
                else:
                    probability_father_passes = PROBS["mutation"]

                probability_mother_passes = None
                if v["mother"] in one_gene:
                    probability_mother_passes = 0.5
                elif v["mother"] in two_genes:
                    probability_mother_passes = (1 - PROBS["mutation"])
                else:
                    probability_mother_passes = PROBS["mutation"]

                probability_copy_of_genes = (probability_father_passes * probability_mother_passes)

        else:
            # probability trait
            if k in have_trait:
                probability_trait = PROBS["trait"][0][True]
            else:
                probability_trait = PROBS["trait"][0][False]

            # probability of genes conditional or unconditional
            if v["father"] == None:
                probability_copy_of_genes = PROBS["gene"][0]
            else:
                probability_father_passes = None
                if v["father"] in one_gene:
                    probability_father_passes = 0.5
                elif v["father"] in two_genes:
                    probability_father_passes = (1 - PROBS["mutation"])
                else:
                    probability_father_passes = PROBS["mutation"]

                probability_mother_passes = None
                if v["mother"] in one_gene:
                    probability_mother_passes = 0.5
                elif v["mother"] in two_genes:
                    probability_mother_passes = (1 - PROBS["mutation"])
                else:
                    probability_mother_passes = PROBS["mutation"]

                probability_copy_of_genes = (1 - probability_mother_passes) * (1 - probability_father_passes)

        if joint_probability_var == None:
            joint_probability_var = probability_copy_of_genes * probability_trait
        else:
            joint_probability_var = joint_probability_var * probability_copy_of_genes * probability_trait

        # print(f"{joint_probability_var:.10f}")

    return joint_probability_var


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for k, v in probabilities.items():
        if k in one_gene:
            v["gene"][1] = v["gene"][1] + p
        elif k in two_genes:
            v["gene"][2] = v["gene"][2] + p
        else:
            v["gene"][0] = v["gene"][0] + p

        if k in have_trait:
            v["trait"][True] = v["trait"][True] + p
        else:
            v["trait"][False] = v["trait"][False] + p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for k, v in probabilities.items():
        s = sum(v["gene"].values())
        v["gene"][0] = v["gene"][0] / s
        v["gene"][1] = v["gene"][1] / s
        v["gene"][2] = v["gene"][2] / s

        s = sum(v["trait"].values())
        v["trait"][True] = v["trait"][True] / s
        v["trait"][False] = v["trait"][False] / s


if __name__ == "__main__":
    main()
