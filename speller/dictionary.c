// Implements a dictionary's functionality
#include <strings.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include "dictionary.h"
#include <stdlib.h>
#include <string.h>
int count = 0;
// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{   int x = 0;
    x = hash(word);
    node *ptr = table[x];
    while (ptr != NULL)
    {
        node *next = ptr->next;
        if(strcasecmp(ptr->word,word)==0)
        {return true;}
        else
        {ptr = next;}
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    int x = 0;
    x = (toupper(word[0]) - 'A');
    return x;

}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{   char word[LENGTH + 1];
    FILE *letter = fopen(dictionary, "r");
    if(letter == NULL)
    {return false;}
    while (fscanf(letter, "%s", word)!= EOF)
    {   int x = 0;
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }
        strcpy(n->word,word);
        x = hash(n->word);
        n->next = table[x];
        table[x] = n;
        count++;
    }
    fclose(letter);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{

    return count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{   int f = 0;
    for (int x=0;x<26;x++)
    {
    node *ptr = table[x];
    while (ptr != NULL)
    {
        node *next = ptr->next;
        free(ptr);
        ptr = next;
    }
    f++;
    }
    if (f > 0)
    {
        return true;
    }
    else
    {
        return false;
    }
}
