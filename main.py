from bs4 import BeautifulSoup
import requests
import csv


def get_nyt_recopies(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    stats_table = soup.find("dl", class_=lambda x: x.startswith("stats_statsTable") if x else False)
    yield_time = stats_table.find("dd", class_="pantry--ui").get_text()
    rating_data = stats_table.find("dd", class_=lambda x: "stats_ratingInfo" in x if x else False)
    rating_data_spans = rating_data.find_all("span")
    rating = rating_data_spans[0].get_text()
    votes = rating_data_spans[-1].get_text().replace('(','').replace(')','')
    notes_section = soup.find(string="All Notes")
    notes = notes_section.parent.next_sibling.get_text().replace('(','').replace(')','').strip()

    date_published_info = soup.find("div", class_=lambda x: x.startswith("datepublished") if x else False).get_text()
    date_published = date_published_info.replace('Updated ', '').replace('Published ', '').strip()

    steps_data = soup.find_all("div", class_=lambda x: "preparation_stepNumber" in x if x else False)
    steps =  len(steps_data)

    ingredients_data = soup.find_all("li", class_=lambda x: "ingredient" in x if x else False)
    ingredients = len(ingredients_data) 

    yield_data = soup.find("div", class_=lambda x: x.startswith("ingredients_recipeYield") if x else False) 
    *_, last_yield_data = yield_data.children
    yield_serving = last_yield_data.get_text()

    next_links = soup.find_all("a", href=lambda x: x.startswith("/recipes") if x else False)
    links = [link['href'] for link in next_links]

    
    print(yield_time, rating, votes, notes, date_published, steps, ingredients, yield_serving)

    
    return {
        "Total Time": yield_time,
        "Rating": rating,
        "Votes": votes,
        "Notes": notes,
        "Date Published": date_published,
        "Steps": steps,
        "Ingredients": ingredients,
        "Serving Size": yield_serving
    }, links

  


if __name__ == '__main__':
    seen_recipes = ["1025274-one-pot-miso-mascarpone-pasta"]
    recipes, links = get_nyt_recopies("https://cooking.nytimes.com/recipes/1025274-one-pot-miso-mascarpone-pasta")

    all_links =  links.copy()


    with open('recipes.csv', mode='w') as file:
        fieldnames = ['Total Time', 'Rating', 'Votes', 'Notes', 'Date Published', 'Steps', 'Ingredients', 'Serving Size']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(recipes)

        count = 0

        # keep iteracting all the links, add new lniks to the list as you go 
        while len(all_links) > 0 and count <= 1000:
            next_link = all_links.pop(0)
            if next_link not in seen_recipes:
                seen_recipes.append(next_link)
                recipe, links = get_nyt_recopies(f"https://cooking.nytimes.com{next_link}")
                writer.writerow(recipe)
                all_links.extend(links)
                print(f"Added {next_link} to the list of recipes")
                count += 1
            
    # print(recipes)
