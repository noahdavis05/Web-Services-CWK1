from lxml import etree

tree = etree.parse("NATX_2025_11_05/FX-PI-01_UK_NATX_LINE-FARE_777_I_Adult-Fare-Inbound-single_2025-11-05_2024-01-26_1848.xml") 
root = tree.getroot()
ns = {'nx': 'http://www.netex.org.uk/netex'}

def get_zone_for_stop(stop_id):
    # get the farezone ID for a given stop. This uses the 'atco.....'
    xpath = f"//nx:FareZone[nx:members/nx:ScheduledStopPointRef[@ref='{stop_id}']]"
    zone = root.xpath(xpath, namespaces=ns)
    if zone:
        return zone[0].get('id')
    return None

def get_fare(origin_naptan, dest_naptan):
    # 1. Map the naptans to fare zones
    origin_zone = get_zone_for_stop(origin_naptan)
    dest_zone = get_zone_for_stop(dest_naptan)
    
    if not origin_zone or not dest_zone:
        return f"Could not find zones for stops: {origin_naptan} -> {dest_naptan}"

    # 2. Get DistanceMatrixElement ID from the zone ids
    xpath_query = (
        f"//nx:DistanceMatrixElement["
        f"nx:StartTariffZoneRef[@ref='{origin_zone}'] and "
        f"nx:EndTariffZoneRef[@ref='{dest_zone}']]"
    )
    element = root.xpath(xpath_query, namespaces=ns)
    
    if not element:
        return f"No route found between zones {origin_zone} and {dest_zone}"
    
    element_id = element[0].get('id')

    # 3. Find the Cell that links this DistanceMatrixElement to a price
    # In your XML, the Cell contains a DistanceMatrixElementPrice which points to our ID
    cell_query = f"//nx:Cell[.//nx:DistanceMatrixElementRef[@ref='{element_id}']]"
    cell = root.xpath(cell_query, namespaces=ns)
    
    if not cell:
        return f"No price cell found for route ID: {element_id}"
    
    # 4. From that cell, get the GeographicalIntervalPriceRef
    price_ref_elem = cell[0].xpath(".//nx:GeographicalIntervalPriceRef", namespaces=ns)
    if not price_ref_elem:
        return "Could not find a price reference in the cell."
    
    price_ref_id = price_ref_elem[0].get('ref')
    
    # 5. Finally, find the GeographicalIntervalPrice with that ID and get the Amount
    amount_query = f"//nx:GeographicalIntervalPrice[@id='{price_ref_id}']/nx:Amount"
    amount = root.xpath(amount_query, namespaces=ns)
    
    if amount:
        return f"Fare: £{amount[0].text}"
    
    return "Price ID found, but no <Amount> tag exists for it."


# Test with your Coventry to Birmingham IDs
print(get_fare('atco:43000005002', 'atco:43002103108'))