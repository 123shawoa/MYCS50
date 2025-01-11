#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

string decrypt(char* str, string key);
int is_safe(char* str);
int is_alphabetical(char *str);
int main (int argc, string argv[])
{
    //condition
    if(argc == 2)
    {
        int x = strlen(argv[1]);
        if (x==26)
        {   string key = argv[1];
            if (is_safe(argv[1])== 1)
            {
            if (is_alphabetical(argv[1]) == 1)
            {

                string plain = get_string("Plaintext:");
                string cipher = decrypt(plain, key);
                printf("ciphertext: %s\n", cipher);

            }
            else
            {
                printf("Contains a number\n");
                return 1;
            }
            }
            else
            {
                printf("repeated letter\n");
                return 1;
            }

        }
        else
        {
            printf("Not enough words\n");
            return 1;

        }

    }
    else
    {
        //fail
        printf("Invalid\n");
        return 1;
    }
}


int is_safe(char *str)
{
    for (int i = 0; str[i] != '\0'; i++)
    {
        for (int j = 0; str[j] != '\0'; j++)
        {
            if (str[i] == str[j] && i != j)
            {
                return 0;
            }
        }
    }
    return 1;
}
int is_alphabetical(char *str)
{
    for (int i = 0; str[i] != '\0'; i++)
    {
        if (!isalpha(str[i]))
        {
            return 0;
        }
    }
    return 1;
}
string decrypt(char* str, string key)
{

        for (int i = 0; str[i] != '\0';)
    {
        if (isalpha(str[i]))
        {   for (int q = 0; key[q] != '\0'; q++)
        {
            if(key[q] == str[i] || (int)key[q] == (int)str[i] - 32 || (int)key[q] == (int)str[i] + 32)
            {
                int asciiValue = (int)str[i];
                int number = asciiValue;
                if (asciiValue > 64 && asciiValue < 91)
                {
                    number = number - 65;
                    int done = (int)key[number];
                    if (done > 96 && done < 123 )
                    {
                        done = done - 32;
                        str[i] = (char) done;
                    }
                    else{str[i] = (char) done;}
                    i = i + 1;
                }
                else if(asciiValue > 96 && asciiValue < 123)
                {
                    number = number - 97;
                    int done = (int)key[number];
                    if (done > 64 && done < 91)
                    {
                        done = done + 32;
                        str[i] = (char) done;
                    }
                    else{str[i] = (char)(done);}
                    i = i + 1;
                }
            }
        }
        }
        else
        {
            i = i+1;
        }
    }
    return str;
}






