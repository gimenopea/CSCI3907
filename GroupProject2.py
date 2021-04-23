#!/usr/bin/env python
# coding: utf-8

# In[1015]:


import re


# ### 1. Open file and assign to variable as a large unicode string

# In[1016]:


file = 'courses.txt'
with open(file,'r', encoding='utf-8') as file:
    text = file.read()


# ### 2. Define functions to identify parts of the string using Regex. Each extract is wrapped in a function for easy debugging

# In[1017]:


#find stars string and match digits before it
def get_course_stars(course_block):
    match = re.search(r'(\d\.\d*) stars', course_block, flags=re.IGNORECASE)
    stars = match.group(1)
    return stars

#find ratings string and match digits before it
def get_course_rating(course_block):
    match = re.search(r'(\d*) ratings', course_block, flags=re.IGNORECASE)
    rating = match.group(1)
    return rating

#find text after ratings string until the next newline character
def get_course_instructor(course_block):
    match = re.search(r'ratings\n\n((.*))\n', course_block, flags=re.IGNORECASE)
    instructor = match.group(1).strip()
    return instructor

#find blob of string after the pattern 'about this course'
def get_course_description(course_block):
    match = re.search(r'about this course\n\n((.*))\n', course_block, flags=re.IGNORECASE)
    desc = match.group(1)
    return desc

#find blob of newline delimitted keywords after the pattern 'skills you will gain'
def get_skills(course_block):
    course_block = course_block.lower()
    return course_block.split('skills you will gain\n')[-1].split('\n')

#generate a key for cypher node variables, remove non alpha chars and remove spaces
def generate_key(text):
    text = re.sub(r'\W+', '', text)
    return text

#cleans text removing parenthesis
def clean_text(text):
    text = text.replace("'", "")
    return text


# ### 3. Define functions to create nodes which can be chained together

# In[1018]:


def create_skill_node(chunk):
    skill_list = []
    for val in chunk['skills']:        
        if val:
            skill_key = generate_key(val)
            if skill_key in skill_keys:
                continue
            else:
                skill_keys.append(skill_key)
                skill_list.append("({}:Skills {{ skill_name: '{}' }})".format(skill_key, clean_text(val)))                
                
    return '\nCREATE '.join(skill_list)
    
                                  
                                  
def create_course_node(chunk):
    course_key = generate_key(chunk['title'])
    if course_key not in course_keys:
        course_keys.append(course_key)
        return 'CREATE ({}:Course {{title: "{}", stars: "{}", num_rating: "{}"}})'.format(course_key,chunk['title'], 
                                                                                 chunk['stars'], 
                                                                                 chunk['rating'])
def create_instructor_node(chunk):
    instructor_key = generate_key(chunk['instructor'])
    if instructor_key not in instructor_keys:
        instructor_keys.append(instructor_key)
        node_string = 'CREATE ({}:Instructor {{ name: "{}"}})'.format(instructor_key, chunk['instructor'])
        return node_string


def create_teach_relationship(chunk):  
    course_key = generate_key(chunk['title'])
    instructor_key = generate_key(chunk['instructor'])
    return 'MERGE ({})-[:TEACHES]->({})'.format(instructor_key, course_key)


def create_course_skill_relationship(chunk):  
    tmp = []
    course_key = generate_key(chunk['title'])
    for val in chunk['skills']:
        if val:
            skill_key = generate_key(val)
            tmp.append('MERGE ({})-[:GAINS]->({})'.format(course_key, skill_key,clean_text(val)))
    return '\n'.join(tmp)


# ### 4. create a master json-like object so we can organize the course attributes and nodes better

# In[1028]:


def create_master_file(text):
    course_master = []

    text_split = text.split("\n\n\n")
    for course in text_split:
        course_dict = {}

        course_dict['title'] = course.split('\n')[0]
        course_dict['stars'] = get_course_stars(course)
        course_dict['rating'] = get_course_rating(course)
        course_dict['instructor'] = get_course_instructor(course)
        course_dict['description'] = get_course_description(course)
        course_dict['skills'] = get_skills(course)

        course_master.append(course_dict)
    
    return course_master


# In[1029]:


#create big course string and inspect the first course
course_master = create_master_file(text)
course_master[0]


# In[1021]:


def write_to_file(cypher_text):
    with open('cypher_file.txt', 'a') as file:
        file.write(cypher_text)
        


# ### 5. Create all skill nodes without duplicates

# In[1022]:


#preview first few skills 
skill_keys = []
for i in course_master[:4]:
    node_string = create_skill_node(i)
    if len(node_string) != 0:
        print('CREATE ' + node_string)

#add to create file
for i in course_master:
    node_string = create_skill_node(i)
    if len(node_string) != 0:        
        write_to_file('CREATE ' + node_string +'\n')


# ### 6. Create all instructor nodes without duplicates

# In[1023]:


#preview first few nodes
instructor_keys = []
for i in course_master[:4]:
    node_string = create_instructor_node(i)
    if node_string:
        print(node_string)

#add to create file
instructor_keys = []
for i in course_master:
    node_string = create_instructor_node(i)
    if node_string:        
        write_to_file(node_string+'\n')
        


# ### 7. Create all course nodes without duplicates

# In[1024]:


#preview the first few courses
course_keys = []
for i in course_master[:4]:
    node_string = create_course_node(i)
    if node_string:
        print(node_string)
    
        
#add to create file
course_keys = []
for i in course_master:
    node_string = create_course_node(i)
    if node_string:        
         write_to_file(node_string+'\n')


# ### 8. Create course-teacher relationships
# 
#     

# In[1025]:


#preview first few relationships
for i in course_master[:4]:
    print(create_teach_relationship(i))
    
    
#add to create file
for i in course_master: 
     write_to_file(create_teach_relationship(i)+'\n')


# ### 9. Create course-skill relationships

# In[1026]:


#preview first few rows
for i in course_master[:4]:
    print(create_course_skill_relationship(i))
    cypher_file.append(create_course_skill_relationship(i))
    
#add to create file
for i in course_master:    
    write_to_file(create_course_skill_relationship(i) + '\n')


# In[1027]:


#file generated is called cypher_file.txt


# In[ ]:




