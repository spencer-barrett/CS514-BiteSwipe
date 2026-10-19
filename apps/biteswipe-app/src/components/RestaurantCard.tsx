import type { Restaurant } from "../lib/types";

export function RestaurantCard({ restaurant }: { restaurant: Restaurant }) {
  const photo = restaurant.photo_urls[0];

  return (
    <article className="relative aspect-3/4 w-full overflow-hidden rounded-2xl bg-muted shadow-xl select-none">
      {photo ? (
        <img
          src={photo}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
          draggable={false}
          loading="eager"
        />
      ) : (
        /* 4 restaurants have no photos. */
        <div className="absolute inset-0 flex items-center justify-center bg-brand/10 p-8">
          <span className="text-center text-4xl font-black tracking-tight text-brand/40">
            {restaurant.name}
          </span>
        </div>
      )}

      <div className="absolute inset-x-0 bottom-0 h-2/3 bg-linear-to-t from-black/90 via-black/50 to-transparent" />

      {/* {restaurant.external_rating !== null && (
        <div className="absolute top-4 right-4 rounded-full bg-black/60 px-3 py-1 text-sm font-semibold text-white backdrop-blur-sm">
          ★ {restaurant.external_rating.toFixed(1)}
          <span className="ml-1 font-normal text-white/70">
            ({restaurant.external_rating_count})
          </span>
        </div>
      )} */}

      <div className="absolute inset-x-0 bottom-0 p-6 text-white">
        <h2 className="text-3xl leading-tight font-black tracking-tight text-balance">
          {restaurant.name}
        </h2>

        <p className="mt-1 text-sm text-white/80">
          {restaurant.address_line1}
          {/* {restaurant.price_level !== null && (
            <span className="ml-2 font-medium text-white">
              {"$".repeat(restaurant.price_level)}
            </span>
          )} */}
        </p>

        {restaurant.cuisines.length > 0 && (
          <ul className="mt-3 flex flex-wrap gap-1.5">
            {restaurant.cuisines.slice(0, 4).map((cuisine) => (
              <li
                key={cuisine}
                className="rounded-full bg-white/15 px-2.5 py-1 text-xs font-medium backdrop-blur-sm"
              >
                {cuisine}
              </li>
            ))}
          </ul>
        )}
      </div>
    </article>
  );
}
