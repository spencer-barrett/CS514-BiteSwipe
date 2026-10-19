export type Restaurant = {
  id: number;
  name: string;
  address_line1: string;
  city: string;
  state: string;
  lat: number;
  lng: number;
  price_level: number | null;
  external_rating: number | null;
  external_rating_count: number;
  cuisines: string[];
  photo_urls: string[];
};

export type SwipedRestaurant = Restaurant & {
  liked: boolean;
  swiped_at: string;
};

export type Swipe = {
  id: number;
  restaurant_id: number;
  liked: boolean;
  created_at: string;
};